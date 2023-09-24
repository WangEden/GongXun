import cv2
# import Functions as F
import numpy as np
from xml.etree import ElementTree as ET
# import serial


# def parseColor(root, thresholdList):
#     root.find('threshold[@tag="ring"]').find('color[@category="red"]')



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

cv2.imshow("maskRed", maskRed)
cv2.imshow("maskGreen", maskGreen)
cv2.imshow("maskBlue", maskBlue)

contours, hierarchy = cv2.findContours(maskRed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
for contour in contours:
    # print(contour)
    rect = cv2.minAreaRect(contour)
    ptrI, (w, h), c = rect



cv2.waitKey(0)
