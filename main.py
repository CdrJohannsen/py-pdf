#!/usr/bin/env python
from helper import DrawType, LineCap, LineJoin
from objects import *
from pdf import PDF


def main():
    pdf = PDF(author="Cdr_Johannsen", subject="Test Page", keywords="Test,Hello World")
    page = pdf.get_page(0)
    content = page.get_content()
    images = page.get_images()
    content.save_state()
    content.set_color_rgb((1, 0.5, 0))
    content.set_width(2)
    content.set_line_cap(LineCap.Round)
    content.set_line_join(LineJoin.Round)
    content.set_dash_pattern(PDFArray([10, 5, 0.01, 5]), 5)
    content.add_rect(100, 40, 40, 40)
    content.draw(DrawType.CloseFillStrokeNonZero)
    helvetica = pdf.fonts.add_font("Helvetica")
    courier = pdf.fonts.add_font("Courier")
    content.add_text(40, 120, "Hello World!", helvetica)
    content.set_color_rgb((0, 0, 0))
    content.add_text(40, 100, "Hello World!", courier, 20)
    content.load_state()
    content.start_path((40, 40))
    content.append_bezier((55, 60), (55, 20), (70, 40))
    content.append_bezier_start((40, 60), (90, 60))
    content.close_path()
    content.set_color_rgb((0, 1, 0.5))
    content.set_color_rgb((1, 0, 0.5), True)
    content.draw(DrawType.CloseFillStrokeNonZero)
    example_image = images.add_image("example/example.png")
    content.set_matrix((0, 0, 0, 0, 10, 200))
    content.save_state()
    content.set_matrix((84, 0, 0, 84, 135.9, 201.239))
    content.set_matrix((0.707106781, -0.707106781, 0.707106781, 0.707106781, 0, 0))
    content.add_image(example_image)
    content.load_state()
    content.add_image(example_image)
    patterns = page.get_patterns()
    tiling = PDFPatternTiling(PDFArray([0, 0, 50, 50]), file=pdf)
    patterns.add_pattern(tiling)
    pdf.write("out.pdf")


if __name__ == "__main__":
    main()
