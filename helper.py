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

class ClipType(Enum):
    NonZero = "W\n"
    OddEven = "W*\n"

class FunctionType(Enum):
    Sampled = 0
    Exponential = 2
    Stitching = 3
    PostScript = 4


class PatternType(Enum):
    Tiling = 1
    Shading = 2


class PaintType(Enum):
    Coloured = 1
    Uncoloured = 2


class TilingType(Enum):
    ConstantSpacing = 1
    NoDistortion = 2
    ConstantSpacingFast = 3


class ShadingType(Enum):
    Function = 1
    Axial = 2
    Radial = 3
    FreeForm = 4
    LatticeForm = 5
    Coons = 6
    Tensor = 7


class PDFUnit(Enum):
    Default = 1.0
    # Inches = 72.0
    # Millimeter = 2.834645669


def pdfify(to_convert) -> str:
    if to_convert is None:
        return "null"
    elif type(to_convert) == str:
        return f"/{to_convert}"
    else:
        return str(to_convert)
