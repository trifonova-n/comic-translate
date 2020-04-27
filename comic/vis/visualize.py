import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patheffects as path_effects
from torch import Tensor
import numpy as np


def show_image(img, ax:plt.Axes=None, figsize:tuple=(3,3), hide_axis:bool=True, cmap:str='viridis',
                alpha:float=None, **kwargs)->plt.Axes:
    """Display `Image` in notebook."""
    if ax is None: fig,ax = plt.subplots(figsize=figsize)
    xtr = dict(cmap=cmap, alpha=alpha, **kwargs)
    ax.imshow(image2np(img.data), **xtr) if (hasattr(img, 'data')) else ax.imshow(img, **xtr)
    if hide_axis: ax.axis('off')
    return ax


def outline(element, linewidth=1):
    element.set_path_effects([path_effects.Stroke(linewidth=linewidth, foreground='black'),
                              path_effects.Normal()])


def image2np(image:Tensor)->np.ndarray:
    "Convert from torch style `image` to numpy/matplotlib style."
    res = image.cpu().permute(1,2,0).numpy()
    return res[...,0] if res.shape[2]==1 else res


def box2wh(box):
    xmin, ymin, xmax, ymax = box
    return xmin, ymin, xmax - xmin, ymax - ymin


def draw_box(ax, box, color):
    x, y, w, h = box2wh(box)
    rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor=color, lw=1)

    patch = ax.add_patch(rect)
    outline(patch, 3)


def draw_mask(ax, mask, color):
    alpha = 0.5
    threshold = 0.05
    my_cmap = cm.jet
    my_cmap.set_under('k', alpha=0)
    my_cmap.set_over(color, alpha=alpha)
    ax.imshow(mask.data.cpu()[:,:], cmap=my_cmap, clim=[threshold, threshold + 0.0001])


def draw_annotation(img, ann, show_masks=False, ax=None, figsize:tuple=(3,3)):
    color_map = {1: (1, 1, 0), 2: (1, 0, 0), 3: (0, 0, 1)}
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    show_image(img, ax=ax, figsize=figsize)
    for i, (box, mask) in enumerate(zip(ann['boxes'], ann['masks'])):
        color = color_map[int(ann['labels'][i])]
        draw_box(ax, box, color)
        if mask.ndim == 3:
            mask = mask[0, :, :]
        draw_mask(ax, mask, color)

    # if 'masks' in ann and show_masks:
    #     for i, mask in enumerate(ann['masks']):
    #         color = color_map[int(ann['labels'][i])]
    #         if mask.ndim == 3:
    #             mask = mask[0, :, :]
    #         draw_mask(ax, mask, color)


