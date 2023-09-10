import cv2
import numpy as np
import picamera
import time

cap = cv2.VideoCapture("/dev/camera0")
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
while True:
    ret, frame = cap.read()
    if ret:
        print(frame)
        cv2.imshow("image", frame)
        cv2.waitKey(1)
        #cv2.imwrite("image.jpg", frame)
        #break
    else:
        print("Fail to read image")
        break
