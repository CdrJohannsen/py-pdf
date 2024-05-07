import os
from datetime import datetime, time
from hashlib import md5

from objects import *


class PDF:
    header: str = "%PDF-1.7\n%¹¹¹¹¹¹¹¹\n\n"
    footer: str = "%%EOF"

    def __init__(
        self,
        *,
        filename: str,
        title: str | None = None,
        subject: str | None = None,
        keywords: str | None = None,
        author: str | None = None,
        creator: str | None = None,
        viewer_preferences: PDFDict | None = None,
        page_layout: str | None = None,
        page_mode: str | None = None,
        lang: str | None = None,
        unit: PDFUnit = PDFUnit.Default,
    ) -> None:
        self.filename = os.path.abspath(filename)
        self.xref_pos = 0
        self.xref = ["0000000000 65535 f "]
        self.id_counter = 1
        self.objects: list[PDFObject] = []
        self.fonts = PDFFonts(file=self)
        self.pages = PDFPages(self, unit=unit.value, count=1)
        root_dict = {
            "Type": "Catalog",
            "Pages": self.pages,
            # PageLabels
            # Names
            # Dests
            # Outlines
            # Threads
            # URI
            # Metadata
            # StructTreeRoot
            # MarkInfo
            # Legal
            # Collection
        }
        if viewer_preferences:
            root_dict["ViewerPreferences"] = viewer_preferences
        if page_layout:
            root_dict["PageLayout"] = page_layout
        if page_mode:
            root_dict["PageMode"] = page_mode
        if lang:
            root_dict["Lang"] = lang

        info_dict = {
            "Producer": PDFString("Py-PDF"),
            "CreationDate": PDFString(datetime.now().strftime("D:%Y%m%d%H%M%S")),
            "ModDate": PDFString(datetime.now().strftime("D:%Y%m%d%H%M%S")),
        }
        if title:
            info_dict["Title"] = PDFString(title)
        if subject:
            info_dict["Subject"] = PDFString(subject)
        if keywords:
            info_dict["Keywords"] = PDFString(keywords)
        if author:
            info_dict["Author"] = PDFString(author)
        if creator:
            info_dict["Creator"] = PDFString(creator)
        self.trailerdict = PDFDict({"Root": PDFDict(root_dict, self), "Info": PDFDict(info_dict, self)})

    def __str__(self) -> str:
        out = self.header
        for obj in self.objects:
            self.xref.append(f"{len(out):0>10} 00000 n ")
            out += obj.to_str()
        self.xref_pos = len(out)
        self.trailerdict["Size"] = self.id_counter

        info_values = "".join(self.trailerdict["Info"].values())
        # This just needs to be unique
        file_id = PDFHex(md5(f"{time()}{self.filename}{self.xref_pos}{info_values}".encode("latin-1")).digest())
        self.trailerdict["ID"] = PDFArray([file_id] * 2)
        out += self._trailer()
        out += self.footer
        return out

    def add_object(self, obj: PDFObject):
        self.objects.append(obj)

    def _trailer(self):
        return f"""xref
0 {self.id_counter}
{"\n".join(self.xref)}
trailer
{self.trailerdict}
startxref
{self.xref_pos}
"""

    def write(self):
        with open(self.filename, "w", encoding="latin-1") as f:
            f.write(self.__str__())

    def get_page(self, index: int) -> PDFPage:
        return self.pages["Kids"][index]
