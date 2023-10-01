import cv2
import Function as F
import numpy as np
from xml.etree import ElementTree as ET
# import serial


# def parseColor(root, thresholdList):
#     root.find('threshold[@tag="ring"]').find('color[@category="red"]')

def print_point(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print("x, y = ", (x, y))

# 声明串口
# uart = serial.Serial(port="/dev/ttyAMA0", 
#                      baudrate=115200, 
#                      bytesize=8, 
#                      parity=serial.PARITY_NONE, 
#                      stopbits=1)

parameterDom = 'threshold.xml'
paraDomRoot = ET.parse(source=parameterDom)
thresholdNode = paraDomRoot.find('threshold[@tag="ring"]')
# print(thresholdNode)

# 红色
redRingColorNode = thresholdNode.find('color[@category="red"]')
red_hsv_max = []
ceilings = redRingColorNode.findall('./*/ceiling')
for ceiling in ceilings:
    red_hsv_max.append(int(ceiling.text))
# print(red_hsv_max)

red_hsv_min = []
floors = redRingColorNode.findall('./*/floor')
for floor in floors:
    red_hsv_min.append(int(floor.text))
# print(red_hsv_min)

red_hsv_min = np.array(red_hsv_min)
red_hsv_max = np.array(red_hsv_max)

# 绿色
greenRingColorNode = thresholdNode.find('color[@category="green"]')
green_hsv_max = []
ceilings = greenRingColorNode.findall('./*/ceiling')
for ceiling in ceilings:
    green_hsv_max.append(int(ceiling.text))
# print(green_hsv_max)

green_hsv_min = []
floors = greenRingColorNode.findall('./*/floor')
for floor in floors:
    green_hsv_min.append(int(floor.text))
# print(green_hsv_min)

# 蓝色
blueRingColorNode = thresholdNode.find('color[@category="blue"]')
blue_hsv_max = []
ceilings = blueRingColorNode.findall('./*/ceiling')
for ceiling in ceilings:
    blue_hsv_max.append(int(ceiling.text))
# print(blue_hsv_max)

blue_hsv_min = []
floors = blueRingColorNode.findall('./*/floor')
for floor in floors:
    blue_hsv_min.append(int(floor.text))
# print(blue_hsv_min)


red_hsv_min = np.array(red_hsv_min)
red_hsv_max = np.array(red_hsv_max)
green_hsv_min = np.array(green_hsv_min)
green_hsv_max = np.array(green_hsv_max)
blue_hsv_min = np.array(blue_hsv_min)
blue_hsv_max = np.array(blue_hsv_max)

img_bgr = cv2.imread('7.jpg')
img_bgr = cv2.pyrMeanShiftFiltering(img_bgr, 15, 20)
img_bgr = cv2.GaussianBlur(img_bgr, (3, 3), 0)
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)


maskRed = cv2.inRange(img_hsv, red_hsv_min, red_hsv_max)
maskGreen = cv2.inRange(img_hsv, green_hsv_min, green_hsv_max)
maskBlue = cv2.inRange(img_hsv, blue_hsv_min, blue_hsv_max)

# cv2.imshow("maskRed", maskRed)
# cv2.imshow("maskGreen", maskGreen)
cv2.imshow("maskBlue", maskBlue)

cv2.waitKey(0)

maskBlue[324:, :] = 0

maskBlue = cv2.medianBlur(maskBlue, 3)
cv2.imshow("maskBlue", maskBlue)
cv2.waitKey(0)
minx, miny = 0, 0
maxx, maxy = maskBlue.shape[1], maskBlue.shape[0]

def mask_find_bboxs(mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8) # connectivity参数的默认值为8
    stats = stats[stats[:,4].argsort()]
    return stats[:-1]

bbox = mask_find_bboxs(maskBlue)
# print(bbox)
for box in bbox:
    x0, y0 = box[0], box[1]
    x1, y1 = box[0] + box[2], box[1] + box[3]
    p1, p2 = (x0, y0), (x1, y1)
    cv2.rectangle(img_bgr, p1, p2, (255, 0 ,0), 1)

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

cameraTop = '/dev/cameraTop'
cameraInc = '/dev/cameraInc'

def task3():
    capTop = F.VideoCapture(cameraTop)
    capInc = F.VideoCapture(cameraInc)




if __name__ == '__main__':
    task3()
    

