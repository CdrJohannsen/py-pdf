id_counter:int = 1

class PyDFObject:
    def __init__(self) -> None:
        global id_counter
        self.id = id_counter
        id_counter += 1

    def __str__(self) -> str:
        return f"{self.id} 0 R"



class PyDFDict(dict):
    def __str__(self) -> str:
        ret = "<<"
        for key, value in self.items():
            ret += f"/{key} /{value}\n"
        ret += ">>"
        return ret
