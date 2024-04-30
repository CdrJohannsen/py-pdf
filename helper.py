from enum import Enum


class LineCap(Enum):
    Butt = 0
    Round = 1
    Square = 2


class LineJoin(Enum):
    Miter = 0
    Round = 1
    Bevel = 2


class DrawType(Enum):
    Stroke = "S\n"
    CloseAndStroke = "s\n"
    FillNonZero = "f\n"
    FillOddEven = "f*\n"
    FillStrokeNonZero = "B\n"
    FillStrokeOddEven = "B*\n"
    CloseFillStrokeNonZero = "b\n"
    CloseFillStrokeOddEven = "b*\n"
    NoOp = "n\n"


def pdfify(to_convert) -> str:
    if to_convert is None:
        return "null"
    elif type(to_convert) == str:
        return f"/{to_convert}"
    else:
        return str(to_convert)
