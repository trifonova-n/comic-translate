import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from fastai.vision import *


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
    return xmin, ymax, xmax - xmin, ymax - ymin


def draw_box(ax, box):
    x, y, w, h = box2wh(box)
    rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor='white', lw=2)
    patch = ax.add_patch(rect)
    outline(patch, 4)


def draw_annotation(img, ann, show_masks=False, ax=None, figsize:tuple=(3,3)):
    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    show_image(img, ax=ax, figsize=figsize)
    for box in ann['boxes']:
        draw_box(ax, box)
