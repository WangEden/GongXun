import cv2
import numpy as np

imgPath = '1.jpg'
img = cv2.imread(imgPath)

cv2.namedWindow("img")
def print_point(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print("x, y = ", (x, y))

roi = (70, 100, 500, 340)
p1 = (70, 100)
p2 = (570, 440)

# cv2.rectangle(img, p1, p2, (255, 0, 0))
cv2.imshow("img", img)
cv2.setMouseCallback("img", print_point)
cv2.waitKey(0)

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("img", img)
cv2.waitKey(0)

# img = cv2.GaussianBlur(img, (3, 3), 0)
# cv2.imshow("img", img)
# cv2.waitKey(0)

img = cv2.blur(img, (3, 3), 1)
cv2.imshow("img", img)
cv2.waitKey(0)

binary = cv2.Canny(img, 50, 70, (3, 3))
# binary = cv2.Sobel(img, cv2.CV_16S, 0, 1)
cv2.imshow("img", binary)
cv2.waitKey(0)

erode_kernel = np.ones((3, 3), dtype=np.uint8)
erosion_binary = cv2.erode(binary, kernel=erode_kernel, iterations=1)

cv2.imshow("img", erosion_binary)
cv2.waitKey(0)