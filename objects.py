import zlib
from typing import Any

from PIL import Image

from helper import *


class PDFObject:
    def __init__(self, *_, file=None) -> None:
        self.file = file
        self.export_seperate = file is not None
        if self.export_seperate and file is not None:
            self.id = file.id_counter
            file.id_counter += 1
            file.add_object(self)

    def __str__(self) -> str:
        if self.export_seperate:
            return f"{self.id} 0 R"
        else:
            return self._get_str()

    def to_str(self) -> str:
        out = f"{self.id} 0 obj\n{self._get_str()}\nendobj\n\n"
        return out

    def _get_str(self) -> str: ...


class PDFColor(PDFObject):
    pdf_name: str


class PDFDict(PDFObject, dict):
    def __init__(self, to_dict={}, file=None):
        dict.__init__(self, to_dict)
        PDFObject.__init__(self, file=file)

    def __str__(self) -> str:
        if self.export_seperate:
            return PDFObject.__str__(self)
        else:
            return self._get_str()

    def _get_str(self) -> str:
        ret = "<<"
        for key, value in self.items():
            if type(value) == str:
                ret += f"/{key}/{value}\n"
            elif type(value) == PDFString:
                ret += f"/{key}{value}\n"
            elif isinstance(value, Enum):
                ret += f"/{key} {value.value}\n"
            elif type(value) == bool:
                ret += f"/{key} {str(value).lower()}\n"
            else:
                ret += f"/{key} {value}\n"
        ret = ret.strip() + ">>"
        return ret


class PDFString(str, PDFObject):
    def __init__(self, string: str) -> None:
        super().__init__(string)

    def __str__(self) -> str:
        return self._get_str()

    def _get_str(self) -> str:
        return f"({super().__str__()})"


class PDFHex(PDFObject):
    def __init__(self, content: int | str | bytes) -> None:
        self.export_seperate = False
        if type(content) == int:
            self.content = f"{content:X}"
        elif type(content) == str:
            self.content = content.encode("latin-1").hex().upper()
        elif type(content) == bytes:
            self.content = content.hex().upper()
        else:
            raise NotImplementedError

    def __str__(self) -> str:
        return self._get_str()

    def _get_str(self) -> str:
        return f"<{self.content}>"


class PDFArray(list, PDFObject):
    def __init__(self, to_list=[], file=None) -> None:
        list.__init__(self, to_list)
        PDFObject.__init__(self, file=file)

    def _get_str(self) -> str:
        return f"[ {' '.join([pdfify(i) for i in self])} ]"


class PDFStream(PDFObject):
    def __init__(self, desc: PDFDict | None = None, *, file) -> None:
        super().__init__(file=file)
        if desc:
            self.desc = desc
        else:
            self.desc = PDFDict()
        self.content = ""
        self.compress = False

    def _get_str(self) -> str:
        self.desc["Length"] = len(self.content)
        if self.compress:
            self.desc["Filter"] = "FlateDecode"
            self.content = zlib.compress(bytes(self.content, encoding="latin-1")).decode("latin-1")
        return f"{self.desc._get_str()}\nstream\n{self.content}\nendstream"


class PDFFunction(PDFDict): ...


class PDFFunctionSampled(PDFStream, PDFFunction):
    def __init__(self, *_, size: PDFArray, bits_per_sample: int, samples: bytes, file=None):
        super().__init__(file=file)
        self.desc["FunctionType"] = FunctionType.Sampled
        self.desc["Domain"] = PDFArray([0, 1, 0, 1])
        self.desc["Size"] = size
        self.desc["Range"] = PDFArray([0, 1, 0, 1, 0, 1])
        self.desc["BitsPerSample"] = bits_per_sample
        self.content = samples.decode("latin-1")


class PDFFunctionExponential(PDFFunction):
    def __init__(self, *_, n: int = 1, c0: PDFArray, c1: PDFArray, file=None):
        super().__init__(file=file)
        self["FunctionType"] = FunctionType.Exponential
        self["Domain"] = PDFArray([0, 1])
        self["N"] = n
        self["C0"] = c0
        self["C1"] = c1


class PDFFunctionPostScript(PDFStream, PDFFunction):
    def __init__(self, *_, script: str, file=None):
        super().__init__(file=file)
        self.desc["FunctionType"] = FunctionType.PostScript
        self.desc["Domain"] = PDFArray([0, 1, 0, 1])
        self.desc["Range"] = PDFArray([0, 1, 0, 1, 0, 1])
        self.content = f"{{\n{script}\n}}"


class PDFColorSpace(PDFArray):
    def __init__(self, spaces: list, pdf_name: str):
        self.pdf_name = pdf_name
        super().__init__()
        self.extend(spaces)


class PDFColorSpaces(PDFDict):
    def __init__(self, file=None):
        PDFObject.__init__(self, file=file)
        self.cs_counter = 1

    def add_colorspace(self, spaces: list) -> PDFColorSpace:
        colorspace = PDFColorSpace(spaces, f"Cs{self.cs_counter}")
        self[f"Cs{self.cs_counter}"] = colorspace
        self.cs_counter += 1
        return colorspace


class PDFFont(PDFDict):
    def __init__(self, name: str, pdf_name: str, file=None):
        self.name = name
        self.pdf_name = pdf_name
        PDFObject.__init__(self, file=file)
        self["Type"] = "Font"
        self["SubType"] = "Type1"
        self["BaseFont"] = name


class PDFFonts(PDFDict):
    def __init__(self, file=None):
        PDFObject.__init__(self, file=file)
        self.font_counter = 1

    def add_font(self, name: str) -> PDFFont:
        font = PDFFont(name, pdf_name=f"F{self.font_counter}", file=self.file)
        self[f"F{self.font_counter}"] = font
        self.font_counter += 1
        return font


class PDFImage(PDFStream):
    def __init__(self, path: str, pdf_name: str, file=None):
        image = Image.open(path)
        self.pdf_name = pdf_name
        PDFStream.__init__(self, file=file)
        self.compress = True
        self.content = image.convert("RGB").tobytes().decode(encoding="latin-1")
        self.desc["Type"] = "XObject"
        self.desc["Subtype"] = "Image"
        self.desc["Width"] = image.width
        self.desc["Height"] = image.height
        self.desc["BitsPerComponent"] = 8
        self.desc["ColorSpace"] = "DeviceRGB"
        self.desc["Interpolate"] = True


class PDFImages(PDFDict):
    def __init__(self, file=None):
        PDFObject.__init__(self, file=file)
        self.image_counter = 1

    def add_image(self, path: str) -> PDFImage:
        image = PDFImage(path, pdf_name=f"Im{self.image_counter}", file=self.file)
        self[f"Im{self.image_counter}"] = image
        self.image_counter += 1
        return image


class PDFGraphicState(PDFDict):
    def __init__(self, to_dict={}, file=None):
        super().__init__(to_dict, file)
        self["Type"] = "ExtGState"


class PDFGraphic(PDFStream):
    def save_state(self):
        self.content += "q\n"

    def load_state(self):
        self.content += "Q\n"

    def set_matrix(self, matrix: tuple[float, float, float, float, float, float]):
        self.content += f"{matrix[0]} {matrix[1]} {matrix[2]} {matrix[3]} {matrix[4]} {matrix[5]} cm\n"

    def set_color_rgb(self, rgb: tuple[float, float, float], stroke: bool = False):
        self.content += f"{rgb[0]} {rgb[1]} {rgb[2]} "
        self.content += "RG\n" if stroke else "rg\n"

    def set_color_gray(self, gray: float, stroke: bool = False):
        self.content += f"{gray} "
        self.content += "G\n" if stroke else "g\n"

    def set_color_cmyk(self, cmyk: tuple[float, float, float, float], stroke: bool = False):
        self.content += f"{cmyk[0]} {cmyk[1]} {cmyk[2]} {cmyk[3]} "
        self.content += "K\n" if stroke else "k\n"

    def set_color(self, c_type: PDFColor, color: tuple | None = None, stroke: bool = False):
        if color is not None:
            self.content += " ".join([str(i) for i in color])
            self.content += " "
        self.content += f"/{c_type.pdf_name} "
        self.content += "SCN\n" if stroke else "scn\n"

    def set_colorspace(self, space: str | PDFColorSpace, stroke: bool = False):
        if isinstance(space, PDFColorSpace):
            self.content += f"/{space.pdf_name} "
        else:
            self.content += f"/{space} "
        self.content += "CS\n" if stroke else "cs\n"

    def set_width(self, width):
        self.content += f"{width} w\n"

    def set_line_cap(self, cap: LineCap):
        self.content += f"{cap.value} j\n"

    def set_line_join(self, join: LineJoin):
        self.content += f"{join.value} J\n"

    def set_miter_limit(self, limit: float):
        self.content += f"{limit} M\n"

    def set_dash_pattern(self, pattern: PDFArray, phase: int = 0):
        self.content += f"{pattern} {phase} d\n"

    def add_rect(self, x: float, y: float, width: float, height: float):
        self.content += f"{x} {y} {width} {height} re\n"

    def draw(self, draw_type: DrawType | ClipType):
        self.content += draw_type.value

    def start_text(self):
        self.content += "BT\n"

    def end_text(self):
        self.content += "ET\n"

    def show_text(
        self,
        text: str | PDFArray,
        newline: bool = False,
        word_spacing: float | None = None,
        char_spacing: float | None = None,
    ):
        if type(text) == str:
            if word_spacing is not None and char_spacing is not None and newline:
                self.content += f'{word_spacing} {char_spacing} ({text}) "\n'
            else:
                self.content += f"({text}) {'Tj' if not newline else '\x27'}\n"
        else:
            self.content += f"{text} TJ\n"

    def add_text(self, x: float, y: float, text: str, font: PDFFont, size: int = 12):
        self.start_text()
        self.set_font(font, size)
        self.set_text_matrix((1, 0, 0, 1, x, y))
        self.show_text(text)
        self.end_text()

    def set_char_spacing(self, spacing: float):
        self.content += f"{spacing} Tc\n"

    def set_word_spacing(self, spacing: float):
        self.content += f"{spacing} Tw\n"

    def set_text_h_scaling(self, scaling: float):
        self.content += f"{scaling} Tz\n"

    def set_leading(self, leading: float):
        self.content += f"{leading} TL\n"

    def set_font(self, font: PDFFont, size: float):
        self.content += f"/{font.pdf_name} {size} Tf\n"

    def set_text_mode(self, mode: TextMode):
        self.content += f"{mode.value} Tr\n"

    def set_text_rise(self, rise: float):
        self.content += f"{rise} Ts\n"

    def add_newline(self, coords: tuple[float, float] | None = None, set_leading: bool = False):
        if coords is None:
            self.content += "T*\n"
        else:
            self.content += f"{coords[0]} {coords[1]} {'TD' if set_leading else 'Td'}\n"

    def set_text_matrix(self, matrix: tuple[float, float, float, float, float, float]):
        self.content += " ".join(map(str, matrix))
        self.content += " Tm\n"

    def start_path(self, start: tuple[float, float]):
        self.content += f"{start[0]} {start[1]} m\n"

    def append_line(self, start: tuple[float, float]):
        self.content += f"{start[0]} {start[1]} l\n"

    def append_bezier(
        self,
        control1: tuple[float, float],
        control2: tuple[float, float],
        end: tuple[float, float],
    ):
        self.content += f"{control1[0]} {control1[1]} {control2[0]} {control2[1]} {end[0]} {end[1]} c\n"

    def append_bezier_start(self, control: tuple[float, float], end: tuple[float, float]):
        self.content += f"{end[0]} {end[1]} {control[0]} {control[1]} v\n"

    def append_bezier_end(self, control: tuple[float, float], end: tuple[float, float]):
        self.content += f"{end[0]} {end[1]} {control[0]} {control[1]} y\n"

    def close_path(self):
        self.content += "h\n"

    def add_image(self, image: PDFImage):
        self.content += f"/{image.pdf_name} Do\n"


class PDFShading(PDFDict): ...


class PDFShadingFunction(PDFShading):
    def __init__(self, *_, function: PDFFunction, matrix: PDFArray, file=None):
        super().__init__(file=file)
        self["ShadingType"] = ShadingType.Function
        self["ColorSpace"] = PDFArray(["DeviceRGB"])
        self["Function"] = function
        self["Matrix"] = matrix


class PDFShadingAxial(PDFShading):
    def __init__(self, *_, coords: PDFArray, function: PDFFunction, file=None):
        super().__init__(file=file)
        self["ShadingType"] = ShadingType.Axial
        self["ColorSpace"] = PDFArray(["DeviceRGB"])
        self["Coords"] = coords
        self["Function"] = function


class PDFShadingRadial(PDFShading):
    def __init__(self, *_, coords: PDFArray, function: PDFFunction, file=None):
        super().__init__(file=file)
        self["ShadingType"] = ShadingType.Radial
        self["ColorSpace"] = PDFArray(["DeviceRGB"])
        self["Coords"] = coords
        self["Function"] = function


class PDFShadingFreeForm(PDFStream, PDFShading):
    def __init__(
        self,
        *_,
        bits_per_coordinate: int,
        bits_per_component: int,
        bits_per_flag: int,
        decode: PDFArray,
        vertices: bytes,
        function: PDFFunction | None = None,
        file=None,
    ):
        super().__init__(file=file)
        self.desc["ShadingType"] = ShadingType.FreeForm
        self.desc["ColorSpace"] = PDFArray(["DeviceRGB"])
        self.desc["BitsPerCoordinate"] = bits_per_coordinate
        self.desc["BitsPerComponent"] = bits_per_component
        self.desc["BitsPerFlag"] = bits_per_flag
        self.desc["Decode"] = decode
        if function is not None:
            self.desc["Function"] = function
        self.content = vertices.decode("latin-1")


class PDFShadingLatticeForm(PDFStream, PDFShading):
    def __init__(
        self,
        *_,
        bits_per_coordinate: int,
        bits_per_component: int,
        vertices_per_row: int,
        decode: PDFArray,
        vertices: bytes,
        function: PDFFunction | None = None,
        file=None,
    ):
        super().__init__(file=file)
        self.desc["ShadingType"] = ShadingType.LatticeForm
        self.desc["ColorSpace"] = PDFArray(["DeviceRGB"])
        self.desc["BitsPerCoordinate"] = bits_per_coordinate
        self.desc["BitsPerComponent"] = bits_per_component
        self.desc["VerticesPerRow"] = vertices_per_row
        self.desc["Decode"] = decode
        if function is not None:
            self.desc["Function"] = function
        self.content = vertices.decode("latin-1")


class PDFShadingCoons(PDFStream, PDFShading):
    def __init__(
        self,
        *_,
        bits_per_coordinate: int,
        bits_per_component: int,
        bits_per_flag: int,
        decode: PDFArray,
        vertices: bytes,
        function: PDFFunction | None = None,
        file=None,
    ):
        super().__init__(file=file)
        self.desc["ShadingType"] = ShadingType.Coons
        self.desc["ColorSpace"] = PDFArray(["DeviceRGB"])
        self.desc["BitsPerCoordinate"] = bits_per_coordinate
        self.desc["BitsPerComponent"] = bits_per_component
        self.desc["BitsPerFlag"] = bits_per_flag
        self.desc["Decode"] = decode
        if function is not None:
            self.desc["Function"] = function
        self.content = vertices.decode("latin-1")


class PDFShadingTensor(PDFStream, PDFShading):
    def __init__(
        self,
        *_,
        bits_per_coordinate: int,
        bits_per_component: int,
        bits_per_flag: int,
        decode: PDFArray,
        vertices: bytes,
        function: PDFFunction | None = None,
        file=None,
    ):
        super().__init__(file=file)
        self.desc["ShadingType"] = ShadingType.Tensor
        self.desc["ColorSpace"] = PDFArray(["DeviceRGB"])
        self.desc["BitsPerCoordinate"] = bits_per_coordinate
        self.desc["BitsPerComponent"] = bits_per_component
        self.desc["BitsPerFlag"] = bits_per_flag
        self.desc["Decode"] = decode
        if function is not None:
            self.desc["Function"] = function
        self.content = vertices.decode("latin-1")


class PDFPattern(PDFGraphic, PDFColor):
    def __init__(self, file=None):
        super().__init__(file=file)
        self.desc["Type"] = "Pattern"

    def set_pdf_name(self, name: str):
        self.pdf_name = name


class PDFPatternShading(PDFPattern):
    def __init__(self, shading: PDFShading, file=None, **kwargs):
        PDFStream.__init__(self, file=file)
        PDFPattern.__init__(self)
        self.export_seperate = True
        self.desc["PatternType"] = PatternType.Shading
        self.desc["Shading"] = shading
        if matrix := kwargs.get("matrix"):
            self.desc["Matrix"] = matrix

    def _get_str(self) -> str:
        return self.desc._get_str()


class PDFPatternTiling(PDFPattern):
    def __init__(
        self,
        box: PDFArray,
        xstep: int | None = None,
        ystep: int | None = None,
        paint_type: PaintType = PaintType.Coloured,
        tiling_type: TilingType = TilingType.NoDistortion,
        file=None,
    ):
        PDFStream.__init__(self, file=file)
        PDFPattern.__init__(self)
        self.export_seperate = True
        self.desc["PatternType"] = PatternType.Tiling
        self.desc["PaintType"] = paint_type
        self.desc["TilingType"] = tiling_type
        self.desc["BBox"] = box
        self.desc["XStep"] = xstep if xstep is not None else box[2]
        self.desc["YStep"] = ystep if ystep is not None else box[3]
        self.desc["Resources"] = PDFDict(file=file)


class PDFPatterns(PDFDict):
    def __init__(self, file=None):
        PDFObject.__init__(self, file=file)
        self.pattern_counter = 1

    def add_pattern(self, pattern: PDFPattern):
        pattern.set_pdf_name(f"P{self.pattern_counter}")
        self[f"P{self.pattern_counter}"] = pattern
        self.pattern_counter += 1


class PDFPage(PDFDict):
    def __init__(self, file, parent, *, unit: float):
        PDFObject.__init__(self, file=file)
        self.images = PDFImages(file=file)
        self.patterns = PDFPatterns(file=file)
        self.colorspaces = PDFColorSpaces(file=file)
        self["Type"] = "Page"
        self["Parent"] = parent
        self["UserUnit"] = unit
        self["MediaBox"] = PDFArray([0, 0, 595.303937007874, 841.889763779528])
        # CropBox
        # BleedBox
        # TrimBox
        # ArtBox
        # Rotate
        # Thumb
        # Annots
        # Metadata
        # StructParents
        desc = PDFDict()
        self["Contents"] = PDFGraphic(desc, file=file)
        self["Resources"] = PDFDict(
            {
                "Font": file.fonts,
                "XObject": self.images,
                "Pattern": self.patterns,
                "ColorSpace": self.colorspaces,
                "ProcSet": PDFArray(["PDF", "Text", "ImageB", "ImageC", "ImageI"]),
                # ExtGState
                # Shading
            },
            file=file,
        )

    def get_content(self) -> PDFGraphic:
        return self["Contents"]

    def get_images(self) -> PDFImages:
        return self.images

    def get_patterns(self) -> PDFPatterns:
        return self.patterns

    def get_colorspaces(self) -> PDFColorSpaces:
        return self.colorspaces


class PDFPages(PDFDict):
    def __init__(self, file, *, unit: float = 1.0, count: int = 1) -> None:
        super().__init__(self, file=file)
        self.parent = file
        self["Type"] = "Pages"
        self["Kids"] = PDFArray()
        self["MediaBox"] = PDFArray([0, 0, 595.303937007874, 841.889763779528])
        for _ in range(count):
            self["Kids"].append(PDFPage(file, self, unit=unit))
        self["Count"] = len(self["Kids"])
