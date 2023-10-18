# from collections import Counter
#
# lis = [(43, 23), (43, 23), (21, 32), (45, 32)]
#
# maxSample = Counter(lis).most_common(2)
# print(maxSample)

import cv2

img = cv2.imread("7.jpg")


def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


img = precondition(img)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("img", gray)
cv2.waitKey(0)
