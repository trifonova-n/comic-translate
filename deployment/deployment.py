from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role

def deploy():
    role = get_execution_role()
    pytorch_model = PyTorchModel(model_data='s3://pytorch-sagemaker-example/model.tar.gz',
                                 role=role,
                                 entry_point='inference.py',
                                 framework_version='1.3.1')

    predictor = pytorch_model.deploy(initial_instance_count=1, instance_type='local')
    return predictor
