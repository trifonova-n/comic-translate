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
        print(name, file=sys.stderr)

        # note that we haven't converted the mask to RGB,
        # because each color corresponds to a different instance
        # with 0 being background
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
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
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
