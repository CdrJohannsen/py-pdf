import zlib
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
            self.content = zlib.compress(
                bytes(self.content, encoding="latin-1")
            ).decode("latin-1")
        return f"{self.desc._get_str()}\nstream\n{self.content}\nendstream"


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
        self.font_counter = 0

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
        self.image_counter = 0

    def add_image(self, path: str) -> PDFImage:
        image = PDFImage(path, pdf_name=f"Im{self.image_counter}", file=self.file)
        self[f"Im{self.image_counter}"] = image
        self.image_counter += 1
        return image


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

    def set_color_cmyk(
        self, cmyk: tuple[float, float, float, float], stroke: bool = False
    ):
        self.content += f"{cmyk[0]} {cmyk[1]} {cmyk[2]} {cmyk[3]} "
        self.content += "K\n" if stroke else "k\n"

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

    def add_rect(self, x: int, y: int, width: int, height: int):
        self.content += f"{x} {y} {width} {height} re\n"

    def draw(self, draw_type: DrawType):
        self.content += draw_type.value

    def add_text(self, x: float, y: float, text: str, font: PDFFont, size: int = 12):
        self.content += f"""BT
/{font.pdf_name} 
{size} Tf
{x} {y} Td
({text}) Tj
ET
"""

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

    def append_bezier_start(
        self, control: tuple[float, float], end: tuple[float, float]
    ):
        self.content += f"{end[0]} {end[1]} {control[0]} {control[1]} v\n"

    def append_bezier_end(self, control: tuple[float, float], end: tuple[float, float]):
        self.content += f"{end[0]} {end[1]} {control[0]} {control[1]} y\n"

    def close_path(self):
        self.content += "h\n"

    def add_image(self, image: PDFImage):
        self.content += f"/{image.pdf_name} Do\n"


class PDFShading(PDFDict):
    def __init__(self, shading_type: ShadingType, file=None):
        super().__init__(file)
        self["ShadingType"] = shading_type
        self["ColorSpace"] = "DeviceRGB"


class PDFPattern(PDFStream):
    def __init__(self, file=None):
        super().__init__(file=file)
        self.desc["Type"] = "Pattern"

    def set_pdf_name(self, name: str):
        self.pdf_name = name


class PDFPatternShading(PDFPattern):
    def __init__(self, file=None):
        super().__init__(file=file)
        self.desc["PatternType"] = PatternType.Shading.value
        self.desc["Shading"] = PDFShading(ShadingType.Axial, file=file)


class PDFPatternTiling(PDFPattern):
    def __init__(self, box: PDFArray, file=None):
        PDFPattern.__init__(self)
        PDFStream.__init__(self, file=file)
        self.desc["PatternType"] = PatternType.Tiling.value
        self.desc["PaintType"] = PaintType.Coloured.value
        self.desc["TilingType"] = TilingType.ConstantSpacing.value
        self.desc["BBox"] = box
        self.desc["XStep"] = box[2]
        self.desc["YStep"] = box[3]
        self.desc["Resources"] = PDFDict()


class PDFPatterns(PDFDict):
    def __init__(self, file=None):
        PDFObject.__init__(self, file=file)
        self.pattern_counter = 0

    def add_pattern(self, pattern: PDFPattern):
        pattern.set_pdf_name(f"P{self.pattern_counter}")
        self[f"P{self.pattern_counter}"] = pattern
        self.pattern_counter += 1


class PDFPage(PDFDict):
    def __init__(self, file, parent, *, unit):
        PDFObject.__init__(self, file=file)
        self.images = PDFImages(file=file)
        self.patterns = PDFPatterns(file=file)
        self["Type"] = "Page"
        self["Parent"] = parent
        self["UserUnit"] = unit
        self["MediaBox"] = PDFArray([0, 0, 595.303937007874, 841.889763779528])
        desc = PDFDict()
        self["Contents"] = PDFGraphic(desc, file=file)
        self["Resources"] = PDFDict(
            {
                "Font": file.fonts,
                "XObject": self.images,
                "Pattern": self.patterns,
                "ProcSet": PDFArray(["PDF", "Text", "ImageB", "ImageC", "ImageI"]),
            },
            file=file,
        )

    def get_content(self) -> PDFGraphic:
        return self["Contents"]

    def get_images(self) -> PDFImages:
        return self.images

    def get_patterns(self) -> PDFPatterns:
        return self.patterns


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
