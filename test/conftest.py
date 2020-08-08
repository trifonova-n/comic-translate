import os
import pathlib
import pytest
import shutil
from skimage.io import imread


def _datadir(request):
    filedir = pathlib.Path(__file__).parent.absolute()
    dir = filedir / '_test_data' / request.node.name
    shutil.rmtree(str(dir), ignore_errors=True)
    os.makedirs(str(dir))
    return dir


@pytest.fixture
def datadir(request):
    """
    Directory for storing test data for latter inspection.
    """
    return _datadir(request)


@pytest.fixture
def data_path():
    """
    Path to a folder with data.
    """
    return pathlib.Path(os.path.abspath(pathlib.Path(__file__) / '..' / '..' / 'data'))


@pytest.fixture
def minidata_path(data_path):
    """
    Path to minidata folder within data.
    """
    return data_path / 'minidata'


@pytest.fixture
def nakaguma_image_path(minidata_path):
    return minidata_path / 'Nakaguma-Talk-1000x543.jpg'


@pytest.fixture
def nakaguma_image(nakaguma_image_path):
    return imread(nakaguma_image_path)
