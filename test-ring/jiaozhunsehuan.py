import cv2
import numpy as np
from Communication import *
from XmlProcess import *


def mask_find_bboxs(mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8) # connectivity参数的默认值为8
    stats = stats[stats[:,4].argsort()]
    return stats[:-1]


color = ['red', 'green', 'blue']
threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
for i, c in enumerate(color):
    xmlReadThreshold("ring", c, threshold[i])


img_bgr = cv2.imread('7.jpg')
img_bgr = cv2.pyrMeanShiftFiltering(img_bgr, 15, 20)
img_bgr = cv2.GaussianBlur(img_bgr, (3, 3), 0)
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

maskRed = cv2.inRange(img_hsv, threshold[0][0], threshold[0][1])
maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
maskBlue = cv2.inRange(img_hsv, threshold[2][0], threshold[2][1])

# cv2.imshow("maskRed", maskRed)
# cv2.imshow("maskGreen", maskGreen)
cv2.imshow("maskBlue", maskBlue)
cv2.waitKey(0)

maskBlue[324:, :] = 0  # 视情况而定

maskBlue = cv2.medianBlur(maskBlue, 3)
cv2.imshow("maskBlue", maskBlue)
cv2.waitKey(0)
minx, miny = 0, 0
maxx, maxy = maskBlue.shape[1], maskBlue.shape[0]

bbox = mask_find_bboxs(maskBlue)
# print(bbox)
for box in bbox:
    x0, y0 = box[0], box[1]
    x1, y1 = box[0] + box[2], box[1] + box[3]
    p1, p2 = (x0, y0), (x1, y1)
    cv2.rectangle(img_bgr, p1, p2, (255, 0, 0), 1)
    print(box)
cv2.imshow("maskRed", img_bgr)
cv2.waitKey(0)

# 找最大box作为roi
bbox = sorted(bbox, key= lambda )
# for box in bbox


# img_bgr = cv2.bitwise_or(img_bgr, img_bgr, maskRed)
cv2.imshow("maskRed", img_bgr)
cv2.waitKey(0)

# if len(maskRed[0]) != 0 and len(maskRed[1]) != 0:
#     minx = np.min(maskRed[1])
#     maxx = np.max(maskRed[1])
#     miny = np.min(maskRed[0])
#     maxy = np.max(maskRed[0])

# rect = [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]
# print(rect)
# cv2.rectangle(img_bgr, rect[0], rect[2], (255, 0, 0), 1)
# cv2.imshow("asd", img_bgr)
# cv2.waitKey(0)

"""
将利用阈值提取出来的掩膜，用于提取出那一部分颜色的图片，具体是进行图片的与操作
截取出那一部分图像，然后在那一部分图像中查找形状，
"""
# kernel = np.ones((3, 3), dtype=np.uint8)
# erode_red_mask = cv2.erode(maskRed, kernel, 1)

# erode_red_mask[324:, :] = 0
# kernel = np.ones((5, 5), dtype=np.uint8)
#
# erode_red_mask = cv2.dilate(erode_red_mask, kernel, 5)
#
# cv2.imshow("erode_red_mask", erode_red_mask)
# cv2.setMouseCallback("erode_red_mask", print_point)

# contours, hierarchy = cv2.findContours(maskRed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# # for contour in contours:
# # print(contours)
# # merge = np.zeros((maskRed.shape[1], maskRed.shape[0]), dtype=np.uint8)
# merge = np.vstack([contours[0], contours[1]])
# for i in range(2, len(contours)):
#     merge = np.vstack([merge, contours[i]])
#
# img = cv2.drawContours(img_bgr, contours, 0, (255, 0, 0), 2)
# cv2.imshow("merge", img)
# cv2.waitKey(0)
#
# rect = cv2.minAreaRect(merge)
# box = cv2.boxPoints(rect)
#
# img = cv2.drawContours(img_bgr, [box], 0, (255, 0, 0), 2)
# cv2.imshow("rect", img)
# merge = np.vstack([contours[0], contours[1]])
# for
    # print(contour)
    # rect = cv2.minAreaRect(contour)
    # ptrI, (w, h), c = rect

cv2.waitKey(0)

# cameraTop = '/dev/cameraTop'
# cameraInc = '/dev/cameraInc'

# def task3():
#     capTop = F.VideoCapture(cameraTop)
#     capInc = F.VideoCapture(cameraInc)





# if __name__ == '__main__':
#     task3()
    

