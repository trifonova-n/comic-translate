import sys
import numpy as np
import torch
import torch.utils.data
import json
from pathlib import Path
from PIL import Image


class ImageTextDataset(torch.utils.data.Dataset):
    def __init__(self, root, transforms=None):
        self.root = Path(root)
        self.transforms = transforms
        # load all image files, sorting them to
        # ensure that they are aligned
        self.masks_dir = self.root / "masks"
        self.imgs = list(sorted((self.root / "images").iterdir()))
        #self.masks = list(sorted((self.root / "masks").iterdir()))
        with (self.root / 'boxes.txt').open() as f:
            self.boxes = json.load(f)

    def __getitem__(self, idx):

        # load images ad masks
        img = Image.open(self.imgs[idx]).convert("RGB")
        name = self.imgs[idx].stem
        mask_files = sorted((self.masks_dir / name).iterdir())

        masks = []
        for mask_file in mask_files:
            mask = Image.open(mask_file)
            mask = np.array(mask)
            mask = mask > 20
            masks.append(mask)
        masks = np.array(masks, dtype=bool)
        # get bounding box coordinates for each mask
        num_objs = len(masks)
        boxes = []
        for i in range(num_objs):
            pos = np.nonzero(masks[i])
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        # there is only one class
        labels = torch.ones((num_objs,), dtype=torch.int64)
        masks = torch.as_tensor(masks, dtype=torch.uint8)

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
        target["masks"] = masks
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.imgs)


class ImageBboxDataset(torch.utils.data.Dataset):
    def __init__(self, root, transforms=None, labels_file='bboxes.txt', label_map=None):
        self.root = Path(root)
        self.transforms = transforms
        # load all image files, sorting them to
        # ensure that they are aligned
        self.imgs = list(sorted((self.root / "images").iterdir()))
        with (self.root / labels_file).open() as f:
            self.bboxes = json.load(f)
        if label_map is None:
            label_map = {'buble': 1, 'text': 2}
        self.label_map = label_map

    def __getitem__(self, idx):

        # load images ad masks
        img = Image.open(self.imgs[idx]).convert("RGB")
        name = self.imgs[idx].stem

        bboxes = []
        labels = []
        for object in self.bboxes[name]:
            xmin = object['left']
            xmax = object['left'] + object['width']
            ymin = object['top']
            ymax = object['top'] + object['height']
            if object['label'] in self.label_map:
                bboxes.append([xmin, ymin, xmax, ymax])
                label = self.label_map[object['label']]
                labels.append(label)

        bboxes = torch.as_tensor(bboxes, dtype=torch.float32)
        # there is only one class
        labels = torch.as_tensor(labels, dtype=torch.int64)
        image_id = torch.tensor([idx])
        if len(bboxes.shape) == 2:
            area = (bboxes[:, 3] - bboxes[:, 1]) * (bboxes[:, 2] - bboxes[:, 0])
        else:
            area = torch.as_tensor([], dtype=torch.float32)
        # suppose all instances are not crowd
        iscrowd = torch.zeros((len(labels),), dtype=torch.int64)

        target = {}
        target["boxes"] = bboxes
        target["labels"] = labels
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.imgs)
