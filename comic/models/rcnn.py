import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
import comic.config as config


def get_model_instance_segmentation(num_classes, rpn_nms_thresh=0.05, pretrained=True):
    # load an instance segmentation model pre-trained pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=pretrained,
                                                               rpn_nms_thresh=rpn_nms_thresh)

    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                       hidden_layer,
                                                       num_classes)

    return model


def get_model_box_detector(num_classes, rpn_nms_thresh=0.05, pretrained=True):
    # load an instance segmentation model pre-trained pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=pretrained,
                                                                 rpn_nms_thresh=rpn_nms_thresh)

    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model


def save_model(model, name):
    config.model_dir.mkdir(exist_ok=True, parents=True)
    torch.save(model.state_dict(), config.model_dir / (name + '.pth'))


def load_model(model, name):
    model.load_state_dict(torch.load(config.model_dir / (name + '.pth')))
    model.eval()
    return model
