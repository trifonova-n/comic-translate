from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role
from pathlib import Path
import shutil
import comic.config as config


def copy_sources(destination):
    dirs = ["models", "utils", "vis"]
    destination = Path(destination) / 'comic'
    for d in dirs:
        shutil.copytree(str(config.project_dir / 'comic' / d), str(destination))


def copy_model(model_path):
    import tarfile
    tar_path = model_path.parent / f'/{model_path.stem}.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as f:
        t = tarfile.TarInfo('models')
        t.type = tarfile.DIRTYPE
        f.addfile(t)
        f.add(model_path, arcname=model_path.name)

    sagemaker_session = sagemaker.Session()
    bucket = sagemaker_session.default_bucket()
    prefix = f'sagemaker/{model_path.stem}'
    model_artefact = sagemaker_session.upload_data(path=str(tar_path), bucket=bucket, key_prefix=prefix)
    return model_artefact

def deploy():
    source = config.project_dir / 'deployment/source'
    entry_point = config.project_dir / 'deployment/serve_text_detector.py'
    copy_sources(source)
    artefact = copy_model(config.model_dir/'text_detector.pth')
    role = get_execution_role()
    pytorch_model = PyTorchModel(model_data=artefact,
                                 role=role,
                                 entry_point=str(entry_point),
                                 source=str(source),
                                 framework_version='1.3.1')

    predictor = pytorch_model.deploy(initial_instance_count=1, instance_type='ml.t2.medium')
    return predictor
