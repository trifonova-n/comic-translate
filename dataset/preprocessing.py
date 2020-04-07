import cv2
import numpy as np


def detect_blobs(image):
    image = 255 - image
    params = cv2.SimpleBlobDetector_Params()

    # Set Area filtering parameters
    params.filterByArea = True
    params.minArea = 1000

    # Set Circularity filtering parameters
    params.filterByCircularity = False
    params.minCircularity = 0.1

    # Set Convexity filtering parameters
    params.filterByConvexity = False
    params.minConvexity = 0.1

    # Set inertia filtering parameters
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs
    keypoints = detector.detect(image)
    print(len(keypoints))

    # Draw blobs on our image as red circles
    blank = np.zeros((1, 1))
    blobs = cv2.drawKeypoints(255 - image, keypoints, blank, (0, 0, 255),
                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return blobs