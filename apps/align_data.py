import cv2
import numpy as np
import argparse
from skimage import io
from pathlib import Path


def align_images(align_path, ref_img_path, output):
    img = io.imread(align_path)
    img_color = cv2.imread(str(align_path))  # Image to be aligned.
    ref_img_color = cv2.imread(str(ref_img_path))  # Reference image.

    # Convert to grayscale.
    img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    ref_img = cv2.cvtColor(ref_img_color, cv2.COLOR_BGR2GRAY)

    height, width = ref_img.shape

    # Create ORB detector with 5000 features.
    orb_detector = cv2.ORB_create(5000)

    # Find keypoints and descriptors.
    # The first arg is the image, second arg is the mask
    #  (which is not reqiured in this case).
    kp1, d1 = orb_detector.detectAndCompute(img, None)
    kp2, d2 = orb_detector.detectAndCompute(ref_img, None)

    # Match features between the two images.
    # We create a Brute Force matcher with
    # Hamming distance as measurement mode.
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match the two sets of descriptors.
    matches = matcher.match(d1, d2)

    # Sort matches on the basis of their Hamming distance.
    matches.sort(key=lambda x: x.distance)

    # Take the top 90 % matches forward.
    matches = matches[:int(len(matches) * 90)]
    no_of_matches = len(matches)

    # Define empty matrices of shape no_of_matches * 2.
    p1 = np.zeros((no_of_matches, 2))
    p2 = np.zeros((no_of_matches, 2))

    for i in range(len(matches)):
        p1[i, :] = kp1[matches[i].queryIdx].pt
        p2[i, :] = kp2[matches[i].trainIdx].pt

        # Find the homography matrix.
    homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)

    # Use this matrix to transform the
    # colored image wrt the reference image.
    transformed_img = cv2.warpPerspective(img_color,
                                          homography, (width, height))

    # Save the output.
    cv2.imwrite(str(output), transformed_img)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='align data from different scans')
    parser.add_argument('align', help='images to be aligned')
    parser.add_argument('--ref', help='reference images')
    parser.add_argument('-o', '--output', help='output folder')
    args = parser.parse_args()

    align_path = Path(args.align)
    ref_path = Path(args.ref)
    out_dir = Path(args.output)
    out_dir.mkdir(exist_ok=True, parents=True)
    for fname in align_path.iterdir():
        if fname.suffix == '.jpg' or fname.suffix == '.png':
            ref_file = ref_path / f'{fname.stem}.jpg'
            if not ref_file.exists():
                ref_file = ref_path / f'{fname.stem}.png'

            align_images(fname, ref_file, out_dir / fname.name)
