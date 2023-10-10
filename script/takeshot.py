import cv2
import numpy as np
import Function as F

#cap = cv2.VideoCapture("/dev/cameraInc")
# cap = cv2.VideoCapture("/dev/cameraTop")
cap = cv2.VideoCapture("/dev/video0")
cap.set(3, 640)
cap.set(4, 480)
# cap.set(cv2.CAP_PROP_AUTO_WB,1)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,1)
# cap.set(cv2.CAP_PROP_EXPOSURE,7)
cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))

n = [0]
with open("img.txt", "r") as file:
    s = file.read()
    n[0] = int(s)
    print(s)

t = n[0]


def capture(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if 5 <= x <= 105 and 20 <= y <= 60:
            n[0] = 0
            print(param[0])
            cv2.imwrite(f"./{n[0]}.jpg", param[0])
            print("click")
            with open("img.txt", "w") as file:
                file.write(str(param[1] + 1))


while n[0] > 0:
    ret, frame = cap.read()
    if ret:
        img_note = frame.copy()
        cv2.rectangle(img_note, (5, 20), (105, 60), (0, 0, 255), 1)
        cv2.putText(img_note, "Capture", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        cv2.imshow("q capture", img_note)
        cv2.setMouseCallback("q capture", capture, [frame, t])
    if cv2.waitKey(10) & 0xFF == ord("q"):
        print(f"img save:{t}.jpg")
        cv2.imwrite(f"./{n[0]}.jpg", frame)
        with open("img.txt", "w") as file:
            file.write(str(t + 1))
        n[0] = 0


