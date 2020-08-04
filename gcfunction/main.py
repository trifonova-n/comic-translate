import sys
import os
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
from google.cloud import storage
import requests, io, logging
from PIL import Image
from comic.models.rcnn import get_model_instance_segmentation
import torch
from torchvision.transforms import functional as F
from pathlib import Path
from comic.utils.filter import filter_outputs
from comic.vis.visualize import box2wh
from flask import jsonify

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


def detect_text(request):
    ## Extracting parameter and returning prediction
    if request.method == 'GET':
        return " Welcome to iris classifier"

    if request.method == 'POST':
        # loading image from url in request
        data = request.get_json()
        image_url = data['image_url']
        img_request = requests.get(image_url, stream=True)
        image = Image.open(io.BytesIO(img_request.content))
        image = F.to_tensor(image)

        logger.info("Calling model")
        with torch.no_grad():
            model.eval()
            out = model(image[None, ...])
        prediction = filter_outputs(out)

        logger.info('Serializing the generated output.')
        ann = prediction[0]
        label_map = {1: 'bubble', 2: 'text'}
        output = {}
        for i, box in enumerate(ann['boxes']):
            box = [int(p) for p in box.data.numpy()]
            pos = box2wh(box)
            output[i] = {'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                         'label': label_map[int(ann['labels'][i])]}
        return jsonify(output)
