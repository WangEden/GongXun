import cv2
import numpy as np

img_path = "10.jpg"

img = cv2.imread(img_path)
cv2.imshow("src", img)
cv2.waitKey(0)
cv2.destroyWindow("src")


