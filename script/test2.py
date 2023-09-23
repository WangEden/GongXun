import cv2
import numpy as np

"""
思路：通过投影变换实时将斜着的圆盘变成正对俯瞰的圆（也可能不需要）
通过创建一个椭圆二值图像，和实时检测到的图像相减，计算匹配情况，匹配度高时检测到
"""

imgPath = '4.jpg'
img = cv2.imread(imgPath)

cv2.namedWindow("img")
def print_point(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print("x, y = ", (x, y))

p1u = (314, 84)
p1l = (107, 198)
p1d = (319, 359)
p1r = (515, 173)

p2u = (315, 32)
p2l = (107, 206)
p2d = (311, 429)
p2r = (526, 190)

srcP = np.array([[314, 84], [107, 198], [319, 359], [515, 173]], dtype=np.float32)
dstP = np.array([[315, 32], [107, 206], [311, 429], [526, 190]], dtype=np.float32)
M = cv2.getPerspectiveTransform(srcP, dstP)

# 显示
# cv2.rectangle(img, p1, p2, (255, 0, 0))
cv2.imshow("img", img)
cv2.setMouseCallback("img", print_point)
cv2.waitKey(0)

# 灰度
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("img", img)
cv2.waitKey(0)

# 投影
# img = cv2.warpPerspective(img, M, (640, 480))
# cv2.imshow("img", img)
# cv2.waitKey(0)
# img_copy = img.copy()

# img = cv2.resize(img, (320, 240))
# cv2.imshow("img", img)
# cv2.waitKey(0)

# 高斯平滑
img = cv2.GaussianBlur(img, (5, 5), 0)
cv2.imshow("img", img)
cv2.waitKey(0)
kernel = np.ones((3,3),np.float32)/9
img = cv2.filter2D(img, -1, kernel)
cv2.imshow("img", img)
cv2.waitKey(0)
# img = cv2.blur(img, (3, 3), 1)
# cv2.imshow("img", img)
# cv2.waitKey(0)

img = cv2.Canny(img, 30, 50, (3, 3))
# binary = cv2.Sobel(img, cv2.CV_16S, 0, 1)

# circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 1, 80, param1=100, param2=20, minRadius=10, maxRadius=0)
# r = circles[0, 0, 2]
# x = circles[0, 0, 0]
# y = circles[0, 0, 1]
# cv2.circle(img, (x, y), r, (255, 0, 0), -1)
cv2.imshow("img", img)
cv2.waitKey(0)

# erode_kernel = np.ones((2, 2), dtype=np.uint8)
# erosion_binary = cv2.erode(img, kernel=erode_kernel, iterations=1)
# cv2.imshow("img", img)
# cv2.waitKey(0)

kernel_2 = np.ones((5, 5), dtype=np.uint8) # 卷积核变为4*4
img = cv2.dilate(img, kernel_2, 1)
cv2.imshow("img", img)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # 轮廓查找

# for contour in contours:
#     # rect = cv2.minAreaRect(contour)
#     # ptrI, (w, h), c = rect
#     print(contour)
#     cv2.drawContours(img_copy, [contour], -1, (255, 90, 60), 2)
#     # cv2.rectangle(img_copy, (int(ptrI[0]), int(ptrI[1])), (int(ptrI[0] + w), int(ptrI[1] + h)), (255, 0, 0), 1)
#     cv2.imshow("img2", img_copy)
#     cv2.waitKey(0)

