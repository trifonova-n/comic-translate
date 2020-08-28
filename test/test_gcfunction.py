import base64
import os
import requests
import re


def test_gcfunction_local(xprocess, localserver, nakaguma_image_path):
    with open(nakaguma_image_path, "rb") as f:
        dataurl = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

    # Send HTTP request simulating Pub/Sub message
    # (GCF translates Pub/Sub messages to HTTP requests internally)
    res = requests.post(
        'http://127.0.0.1:8080',
        json={'image_url': dataurl}
    )
    xprocess.getinfo(localserver).terminate()
    res.raise_for_status()
    res = res.json()
    res = {id: {k: v for k, v in res[id].items() if k != 'mask'} for id in res}
    print('Result: ', res)

    logfile = open(xprocess.getinfo(localserver).logpath, 'r')
    error_data = os.read(logfile.fileno(), 20000).decode("utf-8")
    print(error_data)

    assert not re.search('Traceback', error_data)
