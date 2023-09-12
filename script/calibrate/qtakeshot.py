import cv2
import numpy as np

cap = cv2.VideoCapture("/dev/video2")
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

n = 8
while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        t = 8 - n
        cv2.imwrite(f"./{t}.jpg", frame)
        print(f"take {t} photos")
        n -= 1
