import cv2
import numpy as np

XCenter = 320
YCenter = 240
ROI = [XCenter - 160, YCenter - 160, 320, 320]

p1 = tuple([ROI[0], ROI[1]])
p2 = tuple([ROI[0] + ROI[2], ROI[1] + ROI[3]])

img = cv2.imread("0.jpg")
img_note = img.copy()
cv2.imshow("ckdx", img)
cv2.waitKey(0)

# img = cv2.rectangle(img, p1, p2, (255, 0, 0), 2)
# cv2.imshow("ckdx", img)
# cv2.waitKey(0)

red = [[162, 169, 40], [197, 226, 210]]
green = [[48, 167, 40], [136, 242, 210]]
blue = [[60, 99, 40], [102, 162, 210]]

red = [np.array(red[0]), np.array(red[1])]
green = [np.array(green[0]), np.array(green[1])]
blue = [np.array(blue[0]), np.array(blue[1])]


# for i in target_list:
#     re

img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow("ckdx", img_hsv)
cv2.waitKey(0)

erode_hsv = cv2.erode(img_hsv, None, iterations=2)
cv2.imshow("ckdx", erode_hsv)
cv2.waitKey(0)

mask1 = cv2.inRange(img_hsv, red[0], red[1])
mask2 = cv2.inRange(img_hsv, green[0], green[1])
mask3 = cv2.inRange(img_hsv, blue[0], blue[1])

mask = mask1 + mask2 + mask3
cv2.imshow("casc", mask)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
target_list = []
for c in contours:
    if cv2.contourArea(c) < 4500:  # 过滤掉较面积小的物体
        continue
    else:
        target_list.append(c)

print(len(target_list))
for i in target_list:
    rect = cv2.minAreaRect(i)
    box = cv2.boxPoints(rect)
    print(box)
    cv2.drawContours(img_note, [np.int0(box)], -1, (0, 255, 255), 2)


cv2.imshow("note", img_note)
cv2.waitKey(0)
