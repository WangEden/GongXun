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
print(thresholdNode)

redRingColorNode = thresholdNode.find('color[@category="red"]')
print(redRingColorNode)

red_hsv_max = []
ceilings = redRingColorNode.findall('./*/ceiling')
for ceiling in ceilings:
    red_hsv_max.append(int(ceiling.text))
print(red_hsv_max)

red_hsv_min = []
floors = redRingColorNode.findall('./*/floor')
for floor in floors:
    red_hsv_min.append(int(floor.text))
print(red_hsv_min)

red_hsv_min = np.array(red_hsv_min)
red_hsv_max = np.array(red_hsv_max)

img_bgr = cv2.imread('7.jpg')
img_bgr = cv2.pyrMeanShiftFiltering(img_bgr, 15, 20)
img_bgr = cv2.GaussianBlur(img_bgr, (3, 3), 0)
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(img_hsv, red_hsv_min, red_hsv_max)



cv2.imshow("mask", mask)
cv2.waitKey(0)
print(mask.shape)
