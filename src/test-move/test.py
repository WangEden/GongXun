import cv2
import numpy as np
import time


def moving_detect(frame1, frame2) -> bool:
    img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    grey_diff = cv2.absdiff(img1, img2)  # 计算两幅图的像素差
    change = np.average(grey_diff)
    if change > 4:  # 当两幅图的差异大于给定的值后，认为画面有物体在动
        cv2.putText(frame2, 'moving', (100, 30), 2, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame2, 'quiet', (100, 30), 2, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow("output", frame2)


cap = cv2.VideoCapture("/dev/cameraInc")
ret, frame1 = cap.read()

img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # 将图片转为灰度图，第一个返回值表示是否转换成功，第二个返回值就是灰度图了
start = time.time()
while True:
    end = time.time()
    if end - start > 0.2:  # 每隔2秒拍一幅图，比较前后两幅图的差异
        start = time.time()
        ret, frame1 = cap.read()

    ret, frame2 = cap.read()
    moving_detect(frame1, frame2)
    if cv2.waitKey(5) & 0xFF == ord('q'):  # 按下q停止运行程序
        break
