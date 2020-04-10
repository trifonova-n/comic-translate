import argparse
from numpy.random import Generator, PCG64
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from comic.dataset.dataset_generator import TextGenerator
from comic.models.rcnn import get_model_box_detector, load_model
from torchvision.transforms import functional as F
from comic.dataset import ImageBboxDataset
from comic.vis.visualize import box2wh
import json

bubble_label = 1
text_label = 2


def check_intersection(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return ((x1 <= x2 <= x1 + w1) or (x2 <= x1 <= x2 + w2)) and ((y1 <= y2 <= y1 + h1) or (y2 <= y1 <= y2 + h2))


def check_intersections(boxes, box):
    for b in boxes:
        if check_intersection((b['left'], b['top'], b['width'], b['height']), box):
            return True
    return False


def clip(val, low, high):
    return max(low, min(high, val))


def get_avg_color(img, box):
    colors = []
    dx = 5
    box = [clip(box[0] + dx, 0, img.width - 1),
           clip(box[1] + dx, 0, img.height - 1),
           clip(box[2] - dx, 0, img.width - 1),
           clip(box[3] - dx, 0, img.height - 1)]
    colors.append(img.getpixel((box[0], box[1])))
    colors.append(img.getpixel((box[2], box[3])))
    colors.append(img.getpixel((box[0], box[3])))
    colors.append(img.getpixel((box[2], box[1])))
    color = np.median(colors, axis=0).astype(int)
    return tuple(color)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='align data from different scans')
    parser.add_argument('image_dir', help='images to be aligned')
    parser.add_argument('--text_file', default='data/replics.txt', help='reference images')
    parser.add_argument('-o', '--output', default='data/dataset', help='output folder')
    parser.add_argument('--clean', action='store_true', help='clean texts off images')
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

    if args.clean:
        num_classes = 3
        box_detector = get_model_box_detector(num_classes)
        load_model(box_detector, 'box_detector')

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
        bubbles = []

        if args.clean:
            ann = box_detector(F.to_tensor(image)[None, ...])[0]
            for i, box in enumerate(ann['boxes']):
                box = [int(p) for p in box.data.numpy()]
                if ann['labels'][i] == bubble_label:
                    bubbles.append(box2wh(box))
                    draw = ImageDraw.Draw(image)
                    draw.rectangle(box, fill=get_avg_color(image, box))
                else:
                    pos = box2wh(box)
                    bboxes[name].append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                                         'label': 'text', 'mask': None})
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
            bboxes[name].append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                                 'label': 'text', 'mask': text_number})
            text_number += 1

        with bbox_file_path.open('w') as block_file:
            json.dump(bboxes, block_file, indent=4)
        image.save(out_image_dir / f'{name}.png', format='PNG')
