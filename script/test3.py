import cv2
import numpy as np

filePath = 'test-item.jpg'

img = cv2.imread(filePath)
img = cv2.resize(img, (int(img.shape[1] / 8), (int(img.shape[0] / 8))))

cv2.imshow('src', img)
cv2.waitKey(0)

img_LAB = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.imshow('lab', img_LAB)
cv2.imshow('hsv', img_HSV)
cv2.waitKey(0)

# img_mean =
