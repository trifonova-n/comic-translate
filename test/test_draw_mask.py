from skimage.io import imsave

from comic.models.rcnn import get_model_instance_segmentation
from comic.utils.filter import filter_outputs
from comic.vis import draw_annotation
import torch
import matplotlib.pyplot as plt
from torch import functional as F


def test_draw_annotations(datadir, data_path, nakaguma_image):
    image = torch.FloatTensor(nakaguma_image) / 255
    image = image.transpose(0, 2)
    imsave(datadir / 'input.jpg', nakaguma_image)

    model = get_model_instance_segmentation(num_classes=3, pretrained=False)
    model.load_state_dict(torch.load(data_path / 'model' / 'text_detector.pth', map_location='cpu'))
    model.to('cpu').eval()

    with torch.no_grad():
        model.eval()
        out = model(image[None, ...])
    prediction = filter_outputs(out)
    assert len(prediction) == 1
    assert len(prediction[0]['boxes']) == 12

    fig, ax = plt.subplots(figsize=(15, 15))
    for i, pred in enumerate(prediction):
        draw_annotation(image, pred, ax=ax)
        plt.savefig(datadir / f'annotation_{i}.jpg', bbox_inches='tight')
