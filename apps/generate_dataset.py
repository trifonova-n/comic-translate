import argparse
from numpy.random import Generator, PCG64
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from comic.dataset.dataset_generator import TextGenerator
from comic.models.rcnn import get_model_box_detector, load_model
from torchvision.transforms import functional as F
from comic.utils.bbox import check_intersection, get_avg_color
from comic.vis.visualize import box2wh
import json

bubble_label = 1
text_label = 2


def check_intersections(boxes, box):
    for b in boxes:
        if check_intersection((b['left'], b['top'], b['width'], b['height']), box):
            return True
    return False


def box_from_mask(mask):
    pos = np.nonzero(np.array(mask) > 20)
    if len(pos[0]) == 0:
        return None
    xmin = int(np.min(pos[1]))
    xmax = int(np.max(pos[1]))
    ymin = int(np.min(pos[0]))
    ymax = int(np.max(pos[0]))
    pos = [xmin, ymin, xmax - xmin, ymax - ymin]
    return pos


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
        print(image_path)
        curr_mask_dir = mask_dir / name
        curr_mask_dir.mkdir(exist_ok=True)
        bboxes[name] = []
        bubbles = []
        old_texts = []
        # cleaning text from text bubbles
        if args.clean:
            # use trained net to find text bubbles
            ann = box_detector(F.to_tensor(image)[None, ...])[0]
            for i, box in enumerate(ann['boxes']):
                box = [int(p) for p in box.data.numpy()]
                # clean text if it is inside bubble
                if ann['labels'][i] == bubble_label:
                    bubbles.append(box2wh(box))
                    draw = ImageDraw.Draw(image)
                    draw.rectangle(box, fill=get_avg_color(image, box))
                else:
                    pos = box2wh(box)
                    old_texts.append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                                      'label': 'text', 'mask': None})

        for i in range(len(bubbles) + 10):
            prev_image = image.copy()
            # get box for new generated text
            # first fill bubbles with text, then add several random texts
            if i < len(bubbles):
                x, y, w, h = bubbles[i]
                fancy = False
                label = 'buble'
            else:
                aspect = rg.uniform(0.3, 3)
                w = rg.integers(image.size[0] * 0.05, image.size[0] * 0.25)
                h = int(w / aspect)
                x = int(rg.integers(0, image.width - w))
                y = int(rg.integers(0, image.height * 0.8))
                fancy = True
                label = 'text'
            mask = text_generator.generate(image, (x, y, w, h), fancy=fancy, generate_mask=True)
            pos = box_from_mask(mask)
            # if text is wider then the box, try short text
            if pos is None or pos[2] > w*1.3:
                image = prev_image
                prev_image = image.copy()
                print('short text for box number ', text_number)
                mask = text_generator.generate(image, (x, y, w, h), fancy=fancy, short=True, generate_mask=True)
                pos = box_from_mask(mask)

            if pos is None or pos[2] < 5 or pos[3] < 10 or check_intersections(bboxes[name], pos) or \
                    pos[1] + pos[3] >= image.size[1] or \
                    pos[0] + pos[2] >= image.size[0] or \
                    (i >= len(bubbles) and check_intersections(old_texts, pos)):

                image = prev_image
                print('failed attempt, box number ', text_number)
                continue
            mask.save(curr_mask_dir / f'{text_number:03}.png', format='PNG', compress_level=0)
            bboxes[name].append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                                 'label': label, 'mask': text_number})
            text_number += 1

        for b in old_texts:
            if not check_intersections(bboxes[name], (b['left'], b['top'], b['width'], b['height'])):
                bboxes[name].append(b)

        image.save(out_image_dir / f'{name}.png', format='PNG')

    with bbox_file_path.open('w') as block_file:
        json.dump(bboxes, block_file, indent=4)
