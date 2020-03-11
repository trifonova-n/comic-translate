import numpy as np
import argparse
from numpy.random import Generator, PCG64
from PIL import Image, ImageDraw, ImageFont
from skimage import io
from pathlib import Path
from dataset.dataset_generator import TextGenerator


def check_intersection(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return ((x1 <= x2 <= x1 + w1) or (x2 <= x1 <= x2 + w2)) and ((y1 <= y2 <= y1 + h1) or (y2 <= y1 <= y2 + h2))


def check_intersections(boxes, box):
    for b in boxes:
        if check_intersection(b, box):
            return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='align data from different scans')
    parser.add_argument('image_dir', help='images to be aligned')
    parser.add_argument('--text_file', default='data/replics.txt', help='reference images')
    parser.add_argument('-o', '--output', default='data/dataset', help='output folder')
    args = parser.parse_args()

    image_dir = Path(args.image_dir)
    out_dir = Path(args.output)
    out_dir.mkdir(exist_ok=True, parents=True)
    out_image_dir = out_dir / 'images'
    mask_dir = out_dir / 'masks'
    mask_dir.mkdir(exist_ok=True, parents=True)
    out_image_dir.mkdir(exist_ok=True, parents=True)
    blocks_file_path = out_dir / 'boxes.txt'

    rg = Generator(PCG64())
    text_generator = TextGenerator(args.text_file)
    block_file = blocks_file_path.open('w')

    for image_path in image_dir.glob('**/*'):
        try:
            image = Image.open(image_path).convert('RGB')
        except IOError:
            continue
        num_texts = rg.integers(1, 10)
        name = '_'.join(image_path.relative_to(image_dir).parts[:-1]) + '_' + image_path.stem
        boxes = []
        text_number = 0
        i = 0
        mask = Image.new("L", image.size, 0)
        print(image_path)
        while i < 20 and text_number < num_texts:
            i += 1
            prev_image = image.copy()
            prev_mask = mask.copy()
            pos, mask = text_generator.generate(image, generate_mask=True, mask=mask, mask_color=text_number + 1)

            if check_intersections(boxes, pos):
                image = prev_image
                mask = prev_mask
                print('failed attempt, box number ', text_number)
                continue
            boxes.append(pos)
            text_number += 1

            block_file.write(f'{name}, {pos[0]}, {pos[1]}, {pos[2]}, {pos[3]}\n')
        mask.save(mask_dir / f'{name}.png')
        image.save(out_image_dir / f'{name}.png')
