#!/usr/bin/env python
from helper import DrawType, LineCap, LineJoin
from objects import PDFArray, PDFGraphic
from pdf import PDF


def main():
    pdf = PDF()
    page = pdf.get_page(0).get_content()
    page.set_color((1, 0.5, 0))
    page.set_width(2)
    page.set_line_cap(LineCap.Round)
    page.set_line_join(LineJoin.Round)
    page.set_dash_pattern(PDFArray([0, 15]), 0)
    page.add_rect(40, 40, 50, 50)
    page.draw(DrawType.CloseFillStrokeNonZero)
    page.add_text(400, 400, "Hello World!", list(pdf.fonts.keys())[0])
    pdf.write("out.pdf")


if __name__ == "__main__":
    main()
