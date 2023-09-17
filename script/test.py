import cv2
import numpy as np
import picamera
import time

capL = cv2.VideoCapture("/dev/video0")
capR = cv2.VideoCapture("/dev/video2")
capL.set(3, 640)
capR.set(3, 640)
capL.set(4, 480)
capR.set(4, 480)
capL.set(6, cv2.VideoWriter.fourcc(*'MJPG'))
capR.set(6, cv2.VideoWriter.fourcc(*'MJPG'))
while True:
    retL, frameL = capL.read()
    retR, frameR = capR.read()
    if retL:
        #print(frame)
        cv2.imshow("cameraL", frameL)
        cv2.waitKey(1)
        #cv2.imwrite("image.jpg", frame)
        #break
    else:
        print("Fail")
        break
    if retR:
        cv2.imshow("cameraR", frameR)
        cv2.waitKey(1)
    else:
        print("Fail to read image")
        break
