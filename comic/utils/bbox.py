import numpy as np


def check_intersection_wh(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return ((x1 <= x2 <= x1 + w1) or (x2 <= x1 <= x2 + w2)) and ((y1 <= y2 <= y1 + h1) or (y2 <= y1 <= y2 + h2))


def check_intersection_xy(box1, box2):
    return check_intersection_wh((int(box1[0]), int(box1[1]), int(box1[2] - box1[0]), int(box1[3] - box1[1])),
                                 (int(box2[0]), int(box2[1]), int(box2[2] - box2[0]), int(box2[3] - box2[1])))


def clip(val, low, high):
    return int(max(low, min(high, val)))


def get_avg_color_wh(img, box):
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
