import cv2
import numpy as np


def getCircleCenter(img: np.ndarray):
    result = []
    # img_calc = cv2.GaussianBlur(img, (5, 5), 0)
    img_calc = img
    img_gray = cv2.cvtColor(img_calc, cv2.COLOR_BGR2GRAY)

    img_binary = cv2.adaptiveThreshold(~img_gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
    erode_kernel = np.ones((1, 1), dtype=np.uint8)
    erosion_binary = cv2.erode(img_binary, kernel=erode_kernel, iterations=1)
    # cv2.imshow("video in deal", erosion_binary)
    circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)

    # circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1, 100)
    if circles is not None and len(circles) != 0:
        circles = np.round(circles[0, :]).astype('int')
        for (x, y, r) in circles:
            result.append(tuple([x, y, r]))
    return result


img_path = "img.png"
img = cv2.imread(img_path)
img_note = img.copy()

circles = getCircleCenter(img)
print(circles)

for c in circles:
    cx, cy, r = c
    cv2.circle(img_note, (cx, cy), r, (255, 0, 0), 2)
cv2.imshow("img", img_note)
cv2.waitKey(0)


# # from collections import Counter
# #
# # lis = [(43, 23), (43, 23), (21, 32), (45, 32)]
# #
# # maxSample = Counter(lis).most_common(2)
# # print(maxSample)
#
# import cv2
#
# img = cv2.imread("7.jpg")
#
#
# def precondition(_img):
#     _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
#     _ = cv2.GaussianBlur(_, (3, 3), 0)
#     return _
#
#
# img = precondition(img)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# cv2.imshow("img", gray)
# cv2.waitKey(0)
