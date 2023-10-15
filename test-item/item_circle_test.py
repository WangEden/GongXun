import cv2
import numpy as np


def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(
        _mask, connectivity=8
    )  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


red = [np.array([169, 181, 0]), np.array([185, 220, 255])]
green = [np.array([53, 61, 0]), np.array([88, 179, 255])]
blue = [np.array([83, 103, 0]), np.array([127, 217, 255])]

img = cv2.imread("green.jpg")
cv2.imshow("img", img)
cv2.waitKey(0)

img = precondition(img)
cv2.imshow("img", img)
cv2.waitKey(0)

img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(img, green[0], green[1])
cv2.imshow("img", mask)
cv2.waitKey(0)


