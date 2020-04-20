import sys
import numpy as np
import torch
import torch.utils.data
import json
from pathlib import Path
from PIL import Image


class ImageTextDataset(torch.utils.data.Dataset):
    def __init__(self, root, transforms=None, include_masks=True, label_map=None):
        self.root = Path(root)
        self.transforms = transforms
        self.include_masks = include_masks
        # load all image files, sorting them to
        # ensure that they are aligned
        self.masks_dir = self.root / "masks"
        self.imgs = list(sorted((self.root / "images").iterdir()))
        with (self.root / 'bboxes.txt').open() as f:
            self.boxes = json.load(f)
        if label_map is None:
            label_map = {'buble': 1, 'text': 2}
        self.label_map = label_map

    def __getitem__(self, idx):

        # load images ad masks
        img = Image.open(self.imgs[idx]).convert("RGB")
        name = self.imgs[idx].stem

        boxes, labels, masks = self.read_labels(name, load_mask=self.include_masks)
        num_objs = len(labels)
        image_id = torch.tensor([idx])
        if len(boxes.shape) == 2:
            area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        else:
            area = torch.as_tensor([], dtype=torch.float32)
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        if self.include_masks:
            target["masks"] = masks
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.imgs)

    def read_labels(self, name, load_mask=True):
        bboxes = []
        labels = []
        masks = []
        for object in self.boxes[name]:
            xmin = object['left']
            xmax = object['left'] + object['width']
            ymin = object['top']
            ymax = object['top'] + object['height']
            if object['label'] in self.label_map:
                bboxes.append([xmin, ymin, xmax, ymax])
                label = self.label_map[object['label']]
                labels.append(label)
            if load_mask:
                mask_name = object['mask']
                if mask_name is not None:

                    mask = Image.open(self.masks_dir / name / f'{mask_name:03}.png')
                    mask = np.array(mask)
                    mask = mask > 20
                    masks.append(mask)
        if load_mask:
            bboxes = bboxes[:len(masks)]
            labels = labels[:len(masks)]
            masks = torch.as_tensor(masks, dtype=torch.uint8)

        bboxes = torch.as_tensor(bboxes, dtype=torch.float32)
        # there is only one class
        labels = torch.as_tensor(labels, dtype=torch.int64)

        return bboxes, labels, masks
