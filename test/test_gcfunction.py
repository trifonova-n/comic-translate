import base64
import os
import requests
import re
from unittest.mock import Mock
import resource
import pytest


def test_gcfunction_local(xprocess, localserver, nakaguma_image_path):
    with open(nakaguma_image_path, "rb") as f:
        dataurl = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

    # Send HTTP request simulating Pub/Sub message
    # (GCF translates Pub/Sub messages to HTTP requests internally)
    try:
        res = requests.post(
            'http://127.0.0.1:8080',
            json={'image_url': dataurl}
        )
        res.raise_for_status()
    except Exception as e:
        logfile = open(xprocess.getinfo(localserver).logpath, 'r')
        error_data = os.read(logfile.fileno(), 20000).decode("utf-8")
        print(error_data)
        raise e
    finally:
        xprocess.getinfo(localserver).terminate()
    res = res.json()

    # Check server response
    assert 'boxes' in res
    assert 'background' in res
    boxes = res['boxes']
    assert 'mask' in boxes['0']
    assert len(boxes['0']['mask']) > 100
    res = {id: {k: v for k, v in boxes[id].items() if k != 'mask'} for id in boxes}
    print('Boxes: ', boxes)
    assert '0' in boxes
    assert 'left' in boxes['0']
    assert 'top' in boxes['0']
    assert 'width' in boxes['0']
    assert 'height' in boxes['0']

    logfile = open(xprocess.getinfo(localserver).logpath, 'r')
    error_data = os.read(logfile.fileno(), 20000).decode("utf-8")
    assert not re.search('Traceback', error_data)


@pytest.mark.skip(reason='For debugging only')
def test_detect_text(nakaguma_image_path):
    from flask import Flask
    app = Flask(__name__)
    import gcfunction.main as main
    with open(nakaguma_image_path, "rb") as f:
        dataurl = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    data = {'image_url': dataurl}
    req = Mock(get_json=Mock(return_value=data), method='POST', args=data)
    with app.app_context():
        res = main.detect_text(req)[0].json

    assert 'boxes' in res
    assert 'background' in res
    boxes = res['boxes']
    assert 'mask' in boxes['0']
    assert len(boxes['0']['mask']) > 100
    res = {id: {k: v for k, v in boxes[id].items() if k != 'mask'} for id in boxes}
    print('Boxes: ', boxes)
    assert '0' in boxes
    assert 'left' in boxes['0']
    assert 'top' in boxes['0']
    assert 'width' in boxes['0']
    assert 'height' in boxes['0']
    print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
