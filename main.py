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
    gray_tiling = PDFPatternTiling(PDFArray([0, 0, 20, 20]), paint_type=PaintType.Uncoloured, file=pdf)
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
    function_shading = PDFPatternShading(
        shading=PDFShadingFunction(
            function=PDFFunctionSampled(size=PDFArray([255]), bits_per_sample=8, samples=bytes([]), file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(function_shading)
    content.set_colorspace("Pattern")
    content.set_color(function_shading)
    content.add_rect(0, 500, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    radial_shading = PDFPatternShading(
        shading=PDFShadingRadial(
            coords=PDFArray([125, 350, 20, 165, 350, 30]),
            function=PDFFunctionExponential(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(radial_shading)
    content.set_colorspace("Pattern")
    content.set_color(radial_shading)
    content.add_rect(100, 300, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    axial_shading = PDFPatternShading(
        shading=PDFShadingAxial(
            coords=PDFArray([0, 400, 100, 300]),
            function=PDFFunctionExponential(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(axial_shading)
    content.set_colorspace("Pattern")
    content.set_color(axial_shading)
    content.add_rect(0, 300, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    free_form_shading = PDFPatternShading(
        shading=PDFShadingFreeForm(
            bits_per_coordinate=8,
            bits_per_component=8,
            bits_per_flag=8,
            decode=PDFArray([0, 100, 400, 500, 0, 1, 0, 1, 0, 1]),
            vertices=bytes([0, 255, 255, 0, 0, 255, 0, 0, 255, 255, 0, 0, 0, 255, 0, 255, 255, 0, 1, 0, 0, 0, 255, 0]),
            # function=PDFFunction(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(free_form_shading)
    content.set_colorspace("Pattern")
    content.set_color(free_form_shading)
    content.add_rect(0, 400, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    lattice_form_shading = PDFPatternShading(
        shading=PDFShadingLatticeForm(
            bits_per_coordinate=8,
            bits_per_component=8,
            vertices_per_row=2,
            decode=PDFArray([100, 200, 400, 500, 0, 1, 0, 1, 0, 1]),
            vertices=bytes([255, 255, 0, 0, 255, 0, 255, 255, 0, 0, 255, 0, 255, 255, 0, 0, 0, 0, 255, 0]),
            # function=PDFFunction(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(lattice_form_shading)
    content.set_colorspace("Pattern")
    content.set_color(lattice_form_shading)
    content.add_rect(100, 400, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    coons_shading = PDFPatternShading(
        shading=PDFShadingCoons(
            bits_per_coordinate=8,
            bits_per_component=8,
            bits_per_flag=8,
            decode=PDFArray([200, 300, 400, 500, 0, 1, 0, 1, 0, 1]),
            vertices=bytes(
                [0]
                + [0, 0]
                + [0, 20]
                + [0, 240]
                + [0, 255]
                + [50, 255]
                + [50, 255]
                + [100, 255]
                + [120, 230]
                + [255, 60]
                + [150, 0]
                + [100, 0]
                + [60, 0]
                + [255, 0, 0]
                + [255, 0, 0]
                + [255, 255, 0]
                + [255, 255, 0]
                + [2, 200, 0, 200, 0, 255, 0, 255, 0, 255, 0, 255, 255, 255, 255, 255, 255, 255, 0, 0, 255, 0, 0]
            ),
            # function=PDFFunction(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(coons_shading)
    content.set_colorspace("Pattern")
    content.set_color(coons_shading)
    content.add_rect(200, 400, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    content.save_state()
    tensor_shading = PDFPatternShading(
        shading=PDFShadingTensor(
            bits_per_coordinate=8,
            bits_per_component=8,
            bits_per_flag=8,
            decode=PDFArray([300, 400, 400, 500, 0, 1, 0, 1, 0, 1]),
            vertices=bytes(
                [0]
                + [0, 0]
                + [0, 10]
                + [0, 240]
                + [0, 255]
                + [10, 255]
                + [240, 255]
                + [255, 255]
                + [255, 240]
                + [255, 10]
                + [255, 0]
                + [240, 0]
                + [10, 0]
                + [255, 255]
                + [255, 0]
                + [0, 0]
                + [0, 255]
                + [255, 0, 0]
                + [255, 0, 0]
                + [255, 255, 0]
                + [255, 255, 0]
            ),
            # function=PDFFunction(c0=PDFArray([1, 1, 0]), c1=PDFArray([1, 0.5, 0]), n=2, file=pdf),
            file=pdf,
        ),
        file=pdf,
    )
    patterns.add_pattern(tensor_shading)
    content.set_colorspace("Pattern")
    content.set_color(tensor_shading)
    content.add_rect(300, 400, 100, 100)
    content.draw(DrawType.FillStrokeNonZero)
    content.load_state()

    pdf.write("out.pdf")


if __name__ == "__main__":
    main()
