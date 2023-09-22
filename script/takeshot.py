import cv2
import numpy as np
import Functions as F

cap = cv2.VideoCapture("/dev/cameraInc")
#cap = cv2.VideoCapture("/dev/cameraTop")
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))

n = 0
with open( "img.txt", "r") as file:
    s = file.read()
    n = int(s)
    print(s)

t = n

while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame)
    if cv2.waitKey(10) & 0xFF == ord("q"):
        cv2.imwrite(f"./{n}.jpg", frame)
        print(f"take {n} photo")
        n = 0

with open( "img.txt", "w") as file:
    file.write(str(t+1))
