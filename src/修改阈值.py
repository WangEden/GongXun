from xml.etree import ElementTree
import cv2
import numpy as np
from VisionUtils import *


filename = "./parameterCopy.xml"
img_path = "take.jpg"

# 需要修改的参数 # # # # # # # #
category ="ring"
# category ="item"

# color = "red"
# color = "green"
color = "blue"
# # # # # # # # # # # # # # # #

def callback(event):
    pass


flag = True
change = True

def mouseHandler(e, x, y, f, p):
    global flag, change
    if e == cv2.EVENT_LBUTTONDOWN:
        if x < 50 and y < 50:
            flag = False
        elif x < 50 and 50 < y < 100:
            flag = False
            change = False
        


# 拍摄图片
# cap = VideoCapture("/dev/cameraInc")
cap = VideoCapture(0)
img = cap.read()
cv2.imwrite("take.jpg", img)
cap.terminate()


# 找到结点
paraDomTree = ElementTree.parse(filename)
threshold_node = paraDomTree.find(f'threshold[@tag="{category}"]')
color_node = threshold_node.find(f'color[@category="{color}"]')
floors = color_node.findall('./*/floor')
ceilings = color_node.findall('./*/ceiling')


# 读取图片获取阈值
img = cv2.imread(img_path, 1)
if category == "ring":
    img = cv2.pyrMeanShiftFiltering(img, 15, 20)
img = cv2.GaussianBlur(img, (3, 3), 0)
img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))

img_note = img.copy()
print(img.shape)
mask = np.ones(img.shape, np.uint8) * 255

output = np.hstack([img_note, mask])
cv2.imshow("image", output)

img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.createTrackbar("H_min", "image", 50, 255, callback)
cv2.createTrackbar("H_max", "image", 150, 255, callback)
cv2.createTrackbar("S_min", "image", 0, 255, callback)
cv2.createTrackbar("S_max", "image", 255, 255, callback)
cv2.createTrackbar("V_min", "image", 0, 255, callback)
cv2.createTrackbar("V_max", "image", 255, 255, callback)


cv2.setMouseCallback("image", mouseHandler)
cv2.rectangle(img_note, (0, 0), (50, 50), (255, 0, 0), -1)
cv2.rectangle(img_note, (0, 50), (50, 100), (0, 0, 255), -1)

while flag:
    H_min = cv2.getTrackbarPos("H_min", "image", )
    S_min = cv2.getTrackbarPos("S_min", "image", )
    V_min = cv2.getTrackbarPos("V_min", "image", )
    H_max = cv2.getTrackbarPos("H_max", "image", )
    S_max = cv2.getTrackbarPos("S_max", "image", )
    V_max = cv2.getTrackbarPos("V_max", "image", )

    lower_hsv = np.array([H_min, S_min, V_min])
    upper_hsv = np.array([H_max, S_max, V_max])
    mask = cv2.inRange(img, lower_hsv, upper_hsv)
    mask = np.repeat(mask[:, :, np.newaxis], repeats=3, axis=2)
    output = np.hstack([img_note, mask])
    
    cv2.imshow("image", output)
    if cv2.waitKey(1) & 0XFF == ord('q'):
        break


# 写入阈值
if change:
    floors[0].text = str(H_min)
    floors[1].text = str(S_min)
    floors[2].text = str(V_min)
    ceilings[0].text = str(H_max)
    ceilings[1].text = str(S_max)
    ceilings[2].text = str(V_max)
    paraDomTree.write(filename)
