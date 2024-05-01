#!/usr/bin/env python
from helper import DrawType, LineCap, LineJoin
from objects import *
from pdf import PDF


def main():
    pdf = PDF(author="Cdr_Johannsen", subject="Test Page", keywords="Test,Hello World")
    page = pdf.get_page(0).get_content()
    images = pdf.get_page(0).get_images()
    page.save_state()
    page.set_color_rgb((1, 0.5, 0))
    page.set_width(2)
    page.set_line_cap(LineCap.Round)
    page.set_line_join(LineJoin.Round)
    page.set_dash_pattern(PDFArray([10, 5, 0.01, 5]), 5)
    page.add_rect(100, 40, 40, 40)
    page.draw(DrawType.CloseFillStrokeNonZero)
    helvetica = pdf.fonts.add_font("Helvetica")
    courier = pdf.fonts.add_font("Courier")
    page.add_text(40, 120, "Hello World!", helvetica)
    page.set_color_rgb((0, 0, 0))
    page.add_text(40, 100, "Hello World!", courier, 20)
    page.load_state()
    page.start_path((40, 40))
    page.append_bezier((55, 60), (55, 20), (70, 40))
    page.append_bezier_start((40, 60), (90, 60))
    page.close_path()
    page.set_color_rgb((0, 1, 0.5))
    page.set_color_rgb((1, 0, 0.5), True)
    page.draw(DrawType.CloseFillStrokeNonZero)
    example_image = images.add_image("example/example.png")
    page.set_matrix((0, 0, 0, 0, 10, 200))
    page.save_state()
    page.set_matrix((84, 0, 0, 84, 135.9, 201.239))
    page.set_matrix((0.707106781, -0.707106781, 0.707106781, 0.707106781, 0, 0))
    page.add_image(example_image)
    page.load_state()
    page.add_image(example_image)
    pdf.write("out.pdf")


if __name__ == "__main__":
    main()
