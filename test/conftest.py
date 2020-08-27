import os
import sys
import pathlib
import pytest
import shutil
from skimage.io import imread
from xprocess import ProcessStarter


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


def copy_gcfunction_files(deployment_dir):
    deployment_dir = pathlib.Path(deployment_dir)
    if deployment_dir.exists():
        shutil.rmtree(deployment_dir)
    project_dir = pathlib.Path(__file__).parent.parent
    shutil.copytree(project_dir / 'gcfunction', deployment_dir)
    shutil.copytree(project_dir / 'comic',
                    deployment_dir / 'comic',
                    ignore=shutil.ignore_patterns('comic/dataset/*', 'comic/training/*'))

@pytest.fixture
def localserver(xprocess, request):
    function_name = getattr(request, 'param', 'detect_text')
    server_name = "localserver_" + function_name
    copy_gcfunction_files(xprocess.rootdir / server_name)

    class Starter(ProcessStarter):
        pattern = r"(Booting worker with pid: \d+)|(Traceback)"
        args = [pathlib.Path(sys.executable).parent / 'functions-framework', f'--target={function_name}']
        env = {'GOOGLE_APPLICATION_CREDENTIALS': os.path.abspath(pathlib.Path(__file__).parent.parent / 'comic-translate-github.json'),
               'LC_ALL': 'en_US.utf-8',
               'LANG': 'en_US.utf-8'}

    logfile = xprocess.ensure(server_name, Starter)[1]
    #logfile = open(logfile, 'r')
    #error_data = os.read(logfile.fileno(), 20000)
    #print(error_data.decode("utf-8"))
    #if len(error_data) > 10:
    #    raise Exception(error_data)
    return server_name
