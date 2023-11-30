from xml.etree import ElementTree
import cv2
import numpy as np
from VisionUtils import *

filename = "./parameter.xml"
# filename = "./parameterCopy.xml"
img_path = "take.jpg"

# 需要修改的参数 # # # # # # # #
category ="ring"
# category ="item"

# color = "red"
# color = "green"
color = "blue"
# # # # # # # # # # # # # # # #

flag = True
change = True

def choose_para1(e, x, y, f, p):
    global category, flag
    if e == cv2.EVENT_LBUTTONDOWN:
        if 50 < x < 150 and 50 < y < 100:
            category = "ring"
            flag = False
        elif 200 < x < 300 and 50 < y < 100:
            category = "item"
            flag = False


def choose_para2(e, x, y, f, p):
    global color, flag
    if e == cv2.EVENT_LBUTTONDOWN:
        if 50 < x < 150 and 50 < y < 100:
            color = "red"
            flag = False
        elif 200 < x < 300 and 50 < y < 100:
            color = "green"
            flag = False
        elif 350 < x < 450 and 50 < y < 100:
            color = "blue"
            flag = False


categoryBtn1 = [(50, 50), (150, 100)]
categoryBtn2 = [(200, 50), (300, 100)]


while flag:
    pad = np.ones((480, 640, 3), np.uint8) * 255
    cv2.rectangle(pad, categoryBtn1[0], categoryBtn1[1], (255, 0, 0), 1)
    cv2.rectangle(pad, categoryBtn2[0], categoryBtn2[1], (255, 0, 0), 1)
    cv2.putText(pad, "ring", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
    cv2.putText(pad, "item", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
    cv2.imshow("choose1", pad)
    cv2.setMouseCallback("choose1", choose_para1)
    cv2.waitKey(1)
cv2.destroyAllWindows()
flag = True
print(category)


colorBtn1 = [(50, 50), (150, 100)]
colorBtn2 = [(200, 50), (300, 100)]
colorBtn3 = [(350, 50), (450, 100)]


while flag:
    pad = np.ones((480, 640, 3), np.uint8) * 255
    cv2.rectangle(pad, colorBtn1[0], colorBtn1[1], (255, 0, 0), 1)
    cv2.rectangle(pad, colorBtn2[0], colorBtn2[1], (255, 0, 0), 1)
    cv2.rectangle(pad, colorBtn3[0], colorBtn3[1], (255, 0, 0), 1)
    cv2.putText(pad, f"red", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
    cv2.putText(pad, f"green", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
    cv2.putText(pad, f"blue", (350, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
    cv2.imshow("choose2", pad)
    cv2.setMouseCallback("choose2", choose_para2)
    cv2.waitKey(1)
cv2.destroyAllWindows()
flag = True
print(color)

def callback(event):
    pass


def mouseHandler(e, x, y, f, p):
    global flag, change
    if e == cv2.EVENT_LBUTTONDOWN:
        if 0 < x < 50 and 0 < y < 50:
            flag = False
        elif 0 < x < 50 and 150 < y < 200:
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

img_note = img.copy()
img_note = cv2.resize(img_note, (int(img.shape[1] / 2), int(img.shape[0] / 2)))

print(img.shape)
mask = np.ones(img.shape, np.uint8) * 255
mask = cv2.resize(mask, (int(img.shape[1] / 2), int(img.shape[0] / 2)))

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
cv2.rectangle(img_note, (0, 150), (50, 200), (0, 0, 255), -1)

flag = True
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
    mask = cv2.resize(mask, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
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
