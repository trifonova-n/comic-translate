import argparse
from numpy.random import Generator, PCG64
from PIL import Image
from pathlib import Path
from comic.dataset.dataset_generator import TextGenerator
import json


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
    bbox_file_path = out_dir / 'bboxes.txt'

    rg = Generator(PCG64())
    text_generator = TextGenerator(args.text_file)

    bboxes = {}
    for image_path in image_dir.glob('**/*'):
        try:
            image = Image.open(image_path).convert('RGB')
        except IOError:
            continue
        num_texts = rg.integers(1, 10)
        name = '_'.join(image_path.relative_to(image_dir).parts[:-1]) + '_' + image_path.stem
        text_number = 0
        i = 0
        print(image_path)
        curr_mask_dir = mask_dir / name
        curr_mask_dir.mkdir(exist_ok=True)
        bboxes[name] = []
        while i < 10 and text_number < num_texts:
            i += 1
            prev_image = image.copy()
            pos, mask = text_generator.generate(image, generate_mask=True, mask_color=255)

            if check_intersections(bboxes[name], pos) or \
                    pos[1] + pos[3] >= image.size[1] or \
                    pos[0] + pos[2] >= image.size[0]:
                image = prev_image
                print('failed attempt, box number ', text_number)
                continue
            mask.save(curr_mask_dir / f'{text_number:03}.png', format='PNG', compress_level=0)
            bboxes[name].append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3], 'label': 'text'})
            text_number += 1

        with bbox_file_path.open('w') as block_file:
            json.dump(bboxes, block_file, indent=4)
        image.save(out_image_dir / f'{name}.png', format='PNG')
