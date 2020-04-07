from pathlib import Path
from numpy.random import Generator, PCG64
from PIL import Image, ImageDraw, ImageFont
from utils.text import multiline_text, write_text


class TextGenerator:
    def __init__(self, text_file):
        self.text_list = Path(text_file).open('r+', encoding="utf-8").readlines()
        self.font_files = []
        self.min_font_size = 14
        self.max_font_size = 60
        self.rg = Generator(PCG64())
        self.font_files = list((Path(__file__).parent.absolute() / '../fonts/fancy_fonts').iterdir())

    def generate(self, image, generate_mask=True, mask=None, mask_color=255):
        font_size = self.rg.integers(self.min_font_size, self.max_font_size, endpoint=True)
        font_file = self.rg.choice(self.font_files)
        font = ImageFont.truetype(str(font_file), size=font_size)
        draw = ImageDraw.Draw(image)
        text = self.rg.choice(self.text_list)
        box_width = self.rg.integers(image.size[0]*0.1, image.size[0]*0.8)
        x = int(self.rg.integers(0, image.size[0] - box_width))
        y = int(self.rg.integers(0, image.size[1]*0.8))
        contour = self.rg.choice([0, 1, 2, 3])
        w, h = multiline_text(draw, (x, y), text, box_width, font=font, place='center', color='rgb(0, 0, 0)',
                              contour=contour, contour_color='rgb(255, 255, 255)')

        if generate_mask:
            if mask is None:
                mask = Image.new("L", draw.im.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            multiline_text(mask_draw, (x, y), text, box_width, font=font, place='center', color=mask_color,
                           contour=contour, contour_color=mask_color)
            return (x, y, w, h), mask
        return x, y, w, h
