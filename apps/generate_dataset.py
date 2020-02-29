import numpy as np
import argparse
from numpy.random import Generator, PCG64
from PIL import Image, ImageDraw, ImageFont
from skimage import io
from pathlib import Path
from dataset.dataset_generator import TextGenerator


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
    blocks_file_path = out_dir / 'blocks.txt'

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
        for i in range(num_texts):
            pos, mask = text_generator.generate(image, generate_mask=True)
            block_file.write(f'{name}, {pos[0]}, {pos[1]}, {pos[2]}, {pos[3]}\n')
            mask.save(mask_dir / f'{name}_{i}.png')
        image.save(out_image_dir / f'{name}.png')
