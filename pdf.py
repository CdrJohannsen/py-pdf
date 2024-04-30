from objects import *
from datetime import datetime


class PDF:
    header: str = "%PDF-1.7\n%¹¹¹¹¹¹¹¹\n\n"
    footer: str = "\n%%EOF"

    def __init__(self, *, author: str | None = None,unit:PDFUnit=PDFUnit.Default) -> None:
        self.xref_pos = 0
        self.id_counter = 1
        self.objects: list[PDFObject] = []
        self.fonts = PDFFonts(file=self)
        self.pages = PDFPages(self,unit=unit.value, count=1)
        root_dict = {
            "Type": "Catalog",
            "Pages": self.pages,
            "PageMode": "UseOutlines",
            "OpenAction": PDFArray([self.pages["Kids"][0], "/XYZ", None, None, 0]),
            "Lang": PDFString("de-DE"),
        }
        info_dict = {
            "Producer": PDFString("Py-PDF"),
            "Creator": PDFString("Py-PDF"),
            "CreationDate": PDFString(datetime.now().strftime("D:%Y%m%d%H%M%S")),
            "ModDate": PDFString(datetime.now().strftime("D:%Y%m%d%H%M%S")),
        }
        if author:
            info_dict["Author"] = PDFString(author)
        self.trailerdict = PDFDict({"Size": 18, "Root": PDFDict(root_dict, self), "Info": PDFDict(info_dict, self)})

    def __str__(self) -> str:
        out = self.header
        for obj in self.objects:
            out += obj.to_str()
        out += self._trailer()
        out += self.footer
        return out

    def add_object(self, obj: PDFObject):
        self.objects.append(obj)

    def _trailer(self):
        return f"""xref
0 18
0000000000 65535 f 
trailer
{self.trailerdict}
startxref
{self.xref_pos}
"""

    def write(self, file):
        with open(file, "w") as f:
            f.write(self.__str__())

    def get_page(self, index: int) -> PDFPage:
        return self.pages["Kids"][index]
