from pathlib import Path
from numpy.random import Generator, PCG64
from PIL import Image, ImageDraw, ImageFont
from comic.utils.text import multiline_text
import math
import comic.config as config
from comic.utils.bbox import get_avg_color_wh
import numpy as np


class TextGenerator:
    def __init__(self, text_file):
        with Path(text_file).open('r+', encoding="utf-8") as f:
            self.text_list = [s.rstrip() for s in f.readlines()]
        with (Path(text_file).parent / 'short_replics.txt').open('r+', encoding="utf-8") as f:
            self.short_text_list = [s.rstrip() for s in f.readlines()]
        self.font_files = []
        self.min_font_size = 14
        self.max_font_size = 60
        self.rg = Generator(PCG64())
        self.fancy_fonts = list((config.fonts_dir / 'fancy_fonts').iterdir())
        self.plain_fonts = list((config.fonts_dir / 'fancy_fonts').iterdir())

    def find_font_size(self, text, box, font_file, spacing):
        box_area = box[2]*box[3]
        font = ImageFont.truetype(str(font_file), size=self.min_font_size)
        font_size = font.getsize(text)
        font_area = font_size[0]*(font_size[1] + spacing + 4)
        multiplier = math.sqrt(box_area*0.4 / font_area)
        return int(self.min_font_size*multiplier)

    def generate(self, image, box, fancy=False, short=False, generate_mask=True, mask=None):
        if fancy:
            font_file = self.rg.choice(self.fancy_fonts)
            spacing = 4
        else:
            font_file = self.rg.choice(self.plain_fonts)
            spacing = 2
        text_selected = False
        while not text_selected:
            if short:
                text = self.rg.choice(self.short_text_list)
            else:
                text = self.rg.choice(self.text_list)
            font_size = self.find_font_size(text, box, font_file, spacing=spacing)
            if len(text) < 8 and font_size < self.min_font_size:
                text = '...'
                font_size = self.min_font_size
            if font_size > self.max_font_size:
                font_size = self.max_font_size
            if font_size >= self.min_font_size:
                text_selected = True
        font = ImageFont.truetype(str(font_file), size=font_size)
        draw = ImageDraw.Draw(image)
        x = box[0]
        y = box[1]
        box_width = box[2]
        if fancy:
            contour = self.rg.choice([1, 2, 3])
        else:
            contour = 0
        if self.rg.random() > 0.5:
            text = text.upper()
        bg_color = get_avg_color_wh(image, (box[0], box[1], box[0] + box[2], box[1] + box[3]))
        if np.mean(bg_color) > 128:
            color = (0, 0, 0)
        else:
            color = (255, 255, 255)
        contour_color = (255 - color[0], 255 - color[0], 255 - color[0])
        pos = multiline_text(draw, (x, y), text, box_width, box_height=box[3], font=font, place='center', color=color,
                             contour=contour, contour_color=contour_color, spacing=spacing)
        if generate_mask:
            mask_color = 255
            if mask is None:
                mask = Image.new("L", draw.im.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            multiline_text(mask_draw, (x, y), text, box_width, box_height=box[3], font=font, place='center',
                           color=mask_color, contour=contour, contour_color=mask_color, spacing=spacing)
            return mask
        return pos
