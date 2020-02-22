from pathlib import Path
from numpy.random import Generator, PCG64
from PIL import Image, ImageDraw, ImageFont
from utils.text import multiline_text, write_text


class TextGenerator:
    def __init__(self, text_file):
        self.text_list = Path(text_file).open().readlines()
        self.font_files = []
        self.min_font_size = 10
        self.max_font_size = 60
        self.rg = Generator(PCG64())
        self.font_files = list((Path(__file__).parent.absolute() / '../fonts').iterdir())

    def generate(self, image, generate_mask=False):
        font_size = self.rg.integers(self.min_font_size, self.max_font_size, endpoint=True)
        font_file = self.rg.choice(self.font_files)
        font = ImageFont.truetype(font_file, size=font_size)
        draw = ImageDraw.Draw(image)
        text = self.rg.choice(self.text_list)
        box_width = self.rg.integers(image.size[0]*0.1, image.size[0]*0.8)
        x = self.rg.integers(0, image.size[0] - box_width)
        y = self.rg.integers(0, image.size[1]*0.8)
        contour = self.rg.choice([0, 1, 2, 3])
        w, h = multiline_text(draw, (x, y), text, box_width, font=font, color=(0, 0, 0), contour=contour)
        if generate_mask:
            mask = Image.new("L", draw.im.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            multiline_text(mask_draw, (x, y), text, box_width, font=font, color=(0, 0, 0), contour=contour)
            return (w, h), mask
        return w, h
