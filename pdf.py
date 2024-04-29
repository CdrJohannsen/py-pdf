from helper import *

class PDF:
    header:str = "%PDF-1.7\n%¹¹¹¹¹¹¹¹\n\n"
    footer:str = "\n%%EOF"

    def __init__(self) -> None:
        self.trailerdict=PyDFDict({"Size": 18, "Root":PyDFObject})
        self.xref_pos = 0

    def __str__(self) -> str:
        return self.header + self.trailer() + self.footer

    def trailer(self):
        return f"""
xref
0 18
0000000000 65535 f 
trailer
{self.trailerdict}
startxref
{self.xref_pos}
"""

    def write(self,file):
        with open(file,"w") as f:
            f.write(self.__str__())

