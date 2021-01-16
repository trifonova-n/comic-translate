import os
import sys

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
from google.cloud import storage
import io
import logging
from PIL import Image, ImageDraw
from comic.models.rcnn import get_model_instance_segmentation
import torch
from torchvision.transforms import functional as F
from comic.utils.filter import filter_outputs
from flask import jsonify
import base64
#import numpy
#from scipy.ndimage.morphology import binary_dilation

def box2wh(box):
    xmin, ymin, xmax, ymax = box
    return xmin, ymin, xmax - xmin, ymax - ymin


model = None
device = torch.device('cpu')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if model is None:
    storage_client = storage.Client()

    bucket = storage_client.bucket('comic-translate')
    blob = bucket.blob('models/text_detector.pth')
    blob.download_to_filename('/tmp/text_detector.pth')

    num_classes = 3
    model = get_model_instance_segmentation(num_classes, pretrained=False)
    model.load_state_dict(torch.load('/tmp/text_detector.pth', map_location=device))
    model.to(device).eval()


def encode_image(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        contents = output.getvalue()
    return 'data:image/png;base64,' + base64.b64encode(contents).decode()


def tweak_mask(mask):
    #kernel = numpy.ones((9, 9))
    #mask = binary_dilation(mask, kernel)
    return 1.0*(mask > 0.1)


def encode_mask(mask):
    alpha = F.to_pil_image(mask)
    mask = Image.new("L", alpha.size, 255)
    mask.putalpha(alpha)
    return encode_image(mask)


def inpainting(image_size, annotation):
    new_image = Image.new("RGB", image_size, (255, 255, 255))
    #draw = ImageDraw.Draw(new_image)
    #for k, mask in enumerate(annotation['masks']):
    #    draw.bitmap((0, 0), F.to_pil_image(mask), fill=(255, 255, 255))
    return encode_image(new_image)


def detect_text(request):
    # Extracting parameter and returning prediction
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, PUT, POST',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    if request.method == 'GET':
        return " Welcome to iris classifier"

    if request.method == 'POST':
        headers = {
            'Access-Control-Allow-Origin': '*'
        }

        # loading image from url in request
        data = request.get_json()
        data_url = data['image_url']
        # here parse the data_url out http://xxxxx/?image={dataURL}
        content = data_url.split(';')[1]
        image_encoded = content.split(',')[1]
        body = base64.decodebytes(image_encoded.encode('utf-8'))

        image = Image.open(io.BytesIO(body))
        image_size = image.size
        image = F.to_tensor(image)

        logger.info("Calling model")
        with torch.no_grad():
            model.eval()
            out = model(image[None, ...])
        prediction = filter_outputs(out)
        del out

        logger.info('Serializing the generated output.')
        ann = prediction[0]
        del prediction
        label_map = {1: 'bubble', 2: 'text'}
        boxes = {}
        for i, box in enumerate(ann['boxes']):
            box = [int(p) for p in box.data.numpy()]
            pos = box2wh(box)
            boxes[i] = {'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                         'label': label_map[int(ann['labels'][i])], 'mask': encode_mask(ann['masks'][i])}

        output = {}
        output['boxes'] = boxes
        output['background'] = inpainting(image_size, ann)

        return (jsonify(output), 200, headers)

