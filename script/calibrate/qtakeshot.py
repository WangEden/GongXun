import cv2
import numpy as np

cap = cv2.VideoCapture("/dev/video2")

n = 8
while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cv2.imwrite(f"./{n}.jpg", frame)
        n -= 1