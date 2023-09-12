from utils.Functions import get_circle_center
import numpy as np
import cv2

video_path = '../static/videos/ring/3.mp4'
cap = cv2.VideoCapture(video_path)

while True:
    ret, frame = cap.read()
    if ret:
        ll = get_circle_center(frame)
        for point in ll:
            cv2.circle(frame, point, 3,(0, 255, 0), 4)
        cv2.imshow("video", frame)
        print(ll)
        cv2.waitKey(0)

