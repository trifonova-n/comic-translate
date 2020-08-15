import io
import json
import logging
import requests
from pathlib import Path

import torch
from PIL import Image
from torchvision.transforms import functional as F

from comic.models.rcnn import get_model_instance_segmentation
from comic.utils.filter import filter_outputs
from comic.vis.visualize import box2wh

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

JSON_CONTENT_TYPE = 'application/json'
JPEG_CONTENT_TYPE = 'image/jpeg'


# loads the model into memory from disk and returns it
def model_fn(model_dir):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info('Loading the model.')
    num_classes = 3
    model = get_model_instance_segmentation(num_classes)
    model.load_state_dict(torch.load(Path(model_dir) / 'text_detector.pth'))
    model.to(device).eval()
    logger.info('Done loading model')
    return model


# Deserialize the Invoke request body into an object we can perform prediction on
def input_fn(request_body, content_type=JPEG_CONTENT_TYPE):
    logger.info('Deserializing the input data.')
    image = None
    # process an image uploaded to the endpoint
    if content_type == JPEG_CONTENT_TYPE:
        image = Image.open(io.BytesIO(request_body)).convert("RGB")
    # process a URL submitted to the endpoint
    elif content_type == JSON_CONTENT_TYPE:
        img_request = requests.get(request_body['url'], stream=True)
        image = Image.open(io.BytesIO(img_request.content))
    else:
        raise Exception('Requested unsupported ContentType in content_type: {}'.format(content_type))
    return F.to_tensor(image)


# Perform prediction on the deserialized object, with the loaded model
def predict_fn(input_object, model):
    logger.info("Calling model")
    with torch.no_grad():
        model.eval()
        out = model(input_object[None, ...])
    out = filter_outputs(out)
    return out


# Serialize the prediction result into the desired response content type
def output_fn(prediction, accept=JSON_CONTENT_TYPE):
    logger.info('Serializing the generated output.')
    ann = prediction[0]
    label_map = {'bubble': 1, 'text': 2}
    output = []
    for i, box in enumerate(ann['boxes']):
        box = [int(p) for p in box.data.numpy()]
        pos = box2wh(box)
        output.append({'left': pos[0], 'top': pos[1], 'width': pos[2], 'height': pos[3],
                      'label': label_map[ann['labels'][i]]})
    if accept == JSON_CONTENT_TYPE:
        return json.dumps(prediction), accept
    raise Exception('Requested unsupported ContentType in Accept: {}'.format(accept))
