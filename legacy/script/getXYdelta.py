import cv2
import Function as F
import numpy as np
from xml.etree import ElementTree as ET

parameterDom = 'threshold.xml'
paraDomRoot = ET.parse(source=parameterDom)
thresholdNode = paraDomRoot.find('threshold[@tag="ring"]')
# 红色
red_hsv_max = []
red_hsv_min = []
# 绿色
green_hsv_max = []
green_hsv_min = []
# 蓝色
blue_hsv_max = []
blue_hsv_min = []

def getColorThershold(root, tag, max, min):
    colorNode = root.find(f'color[@category="{tag}"]')
    ceilings = colorNode.findall('./*/ceiling')
    floors = colorNode.findall('./*/floor')
    for i in range(3):
        max.append(int(ceilings[i].text))
        min.append(int(floors[i].text))


def getXYDelta():
    pass


if __name__ == "__main__":
    getColorThershold(thresholdNode, 'red', red_hsv_max, red_hsv_min)
    getColorThershold(thresholdNode, 'green', green_hsv_max, green_hsv_min)
    getColorThershold(thresholdNode, 'blue', blue_hsv_max, blue_hsv_min)


