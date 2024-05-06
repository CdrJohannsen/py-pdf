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
    content.save_state()
    content.start_path((40, 40))
    content.append_bezier((55, 60), (55, 20), (70, 40))
    content.append_bezier_start((40, 60), (90, 60))
    content.close_path()
    content.set_color_rgb((1, 0.8, 0))
    content.set_color_rgb((1, 0, 0.5), True)
    content.draw(DrawType.CloseFillStrokeNonZero)
    example_image = images.add_image("example/example.png")
    content.load_state()
    content.save_state()
    content.set_matrix((84, 0, 0, 84, 100, 200))
    content.set_matrix((0.707106781, -0.707106781, 0.707106781, 0.707106781, 0, 0))
    content.add_image(example_image)
    content.load_state()
    patterns = page.get_patterns()
    tiling = PDFPatternTiling(PDFArray([0, 0, 20, 20]), file=pdf)
    tiling.save_state()
    tiling.set_color_rgb((1, 0.6, 0))
    tiling.set_width(2)
    tiling.add_rect(5, 5, 10, 10)
    tiling.draw(DrawType.FillStrokeNonZero)
    tiling.load_state()
    patterns.add_pattern(tiling)
    content.save_state()
    content.set_colorspace("Pattern")
    content.set_color(tiling)
    content.add_rect(300, 300, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()
    content.save_state()
    cs = page.get_colorspaces()
    rgb = cs.add_colorspace(["Pattern", "DeviceRGB"])
    gray_tiling = PDFPatternTiling(
        PDFArray([0, 0, 20, 20]), paint_type=PaintType.Uncoloured, file=pdf
    )
    gray_tiling.save_state()
    gray_tiling.set_width(2)
    gray_tiling.add_rect(5, 5, 10, 10)
    gray_tiling.draw(DrawType.FillStrokeNonZero)
    gray_tiling.load_state()
    patterns.add_pattern(gray_tiling)
    content.set_colorspace(rgb)
    content.set_color(gray_tiling, (1, 0.6, 0))
    content.add_rect(200, 300, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()
    content.save_state()

    shading = PDFPatternShading(
        shading_type=ShadingType.Radial,
        coords=PDFArray([0, 0, 1, 0, 0, 50]),
        function=PDFFunction(file=pdf),
        matrix=PDFArray([0.50002, 0, 0, 0.500021, 224.389, 397.414]),
        file=pdf,
    )
    patterns.add_pattern(shading)
    content.set_colorspace("Pattern")
    content.set_color(shading)
    content.add_rect(100, 300, 100, 100)
    content.draw(DrawType.FillNonZero)
    content.load_state()

    pdf.write("out.pdf")


if __name__ == "__main__":
    main()
