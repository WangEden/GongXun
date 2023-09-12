import numpy as np
import cv2
import utils.Functions as F


video_path = '../static/videos/ring/5.mp4'
cap = cv2.VideoCapture(video_path)
lis = []
k = 2
last_frame = None

while True:
    ret, frame = cap.read()
    if ret:
        frame = F.unDistort(frame)
        ll = F.get_circle_center(frame)
        for point in ll:
            cv2.circle(frame, point, 3,(0, 255, 0), 4)
            lis.append([point[0], point[1]])
        cv2.imshow("video", frame)
        if len(lis) > 99:
            last_frame = frame
            break
        cv2.waitKey(1)

centers = F.get_kmeans_center(2, lis)

for point in centers:
    p = np.round(point, 0).astype(int)
    p = tuple(p.tolist())
    print(type(p), p)
    cv2.circle(last_frame, p, 3, (0, 0, 255), 4)

cv2.imshow("result", last_frame)
cv2.waitKey(0)
