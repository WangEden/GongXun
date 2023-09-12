import cv2
import numpy as np
import Functions as F

cap = cv2.VideoCapture("/dev/video2")
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

n = 1
while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cv2.imwrite(f"./{n}.jpg", frame)
        print(f"take {n} photo")
        n -= 1
