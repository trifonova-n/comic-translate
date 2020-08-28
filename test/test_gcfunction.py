import base64
import os
import requests
import re


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
    finally:
        xprocess.getinfo(localserver).terminate()
    res.raise_for_status()
    res = res.json()

    # Check server response
    assert 'mask' in res['0']
    assert len(res['0']['mask']) > 100
    res = {id: {k: v for k, v in res[id].items() if k != 'mask'} for id in res}
    print('Result: ', res)
    assert '0' in res
    assert 'left' in res['0']
    assert 'top' in res['0']
    assert 'width' in res['0']
    assert 'height' in res['0']

    logfile = open(xprocess.getinfo(localserver).logpath, 'r')
    error_data = os.read(logfile.fileno(), 20000).decode("utf-8")
    print(error_data)

    assert not re.search('Traceback', error_data)
