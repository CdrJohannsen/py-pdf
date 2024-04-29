from objects import *


class PDF:
    header: str = "%PDF-1.7\n%¹¹¹¹¹¹¹¹\n\n"
    footer: str = "\n%%EOF"

    def __init__(self) -> None:
        self.xref_pos = 0
        self.id_counter = 1
        self.objects: list[PDFObject] = []
        self.fonts = PDFFonts(file=self)
        self.fonts.add_font("Helvetica")
        self.pages = PDFPages(self, 1)
        root_dict = {
            "Type": "Catalog",
            "Pages": self.pages,
            "PageMode": "UseOutlines",
            "OpenAction": PDFArray([self.pages["Kids"][0], "/XYZ", None, None, 0]),
            "Lang": PDFString("de-DE"),
        }
        self.trailerdict = PDFDict({"Size": 18, "Root": PDFDict(root_dict, self)})

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
