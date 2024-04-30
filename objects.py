from typing import Any

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
    def __init__(self, desc: PDFDict, *, file) -> None:
        super().__init__(file=file)
        self.desc = desc
        self.content = ""

    def _get_str(self) -> str:
        self.desc["Length"] = len(self.content)
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
        return font


class PDFGraphic(PDFStream):
    def save_state(self):
        self.content += "q\n"

    def load_state(self):
        self.content += "Q\n"

    def set_color(self, rgb: tuple[float, float, float]):
        self.content += f"{rgb[0]} {rgb[1]} {rgb[2]} rg\n"

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


class PDFPage(PDFDict):
    def __init__(self, file, parent):
        PDFObject.__init__(self, file=file)
        self["Type"] = "Page"
        self["Parent"] = parent
        self["MediaBox"] = PDFArray([0, 0, 595.303937007874, 841.889763779528])
        desc = PDFDict()
        self["Contents"] = PDFGraphic(desc, file=file)
        self["Resources"] = PDFDict(
            {"Font": file.fonts, "ProcSet": PDFArray(["PDF", "Text", "ImageB", "ImageC", "ImageI"])}, file=file
        )

    def get_content(self) -> PDFGraphic:
        return self["Contents"]


class PDFPages(PDFDict):
    def __init__(self, file, count: int = 1) -> None:
        super().__init__(self, file=file)
        self.parent = file
        self["Type"] = "Pages"
        self["Kids"] = PDFArray()
        self["MediaBox"] = PDFArray([0, 0, 595.303937007874, 841.889763779528])
        for _ in range(count):
            self["Kids"].append(PDFPage(file, self))
        self["Count"] = len(self["Kids"])
