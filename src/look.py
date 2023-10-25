import cv2
import time
import numpy as np


video_file = "./videos/video.mp4"
cap = cv2.VideoCapture(0)  # 读取视频文件，参数设置为0表示从摄像头获取图像


def moving_detect(frame1, frame2):
    img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    grey_diff = cv2.absdiff(img1, img2)  # 计算两幅图的像素差
    change = np.average(grey_diff)

    if change > 10:  # 当两幅图的差异大于给定的值后，认为画面有物体在动
        cv2.putText(frame2, 'moving', (100, 30), 2, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame2, 'quiet', (100, 30), 2, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow("output", frame2)


_, frame1 = cap.read()
img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # 将图片转为灰度图，第一个返回值表示是否转换成功，第二个返回值就是灰度图了
start = time.time()
while True:
    end = time.time()
    if (end - start > 0.1):  # 每隔2秒拍一幅图，比较前后两幅图的差异
        start = time.time()
        _, frame1 = cap.read()

    _, frame2 = cap.read()
    moving_detect(frame1, frame2)
    if cv2.waitKey(5) & 0xFF == ord('q'):  # 按下q停止运行程序
        break


# 最后，关闭所有窗口
cap.release()
cv2.destroyAllWindows()

# import cv2
# import numpy as np
#
#
# cap = cv2.VideoCapture("/dev/cameraInc")
# cap.set(3, 640)
# cap.set(4, 480)
# cap.set(cv2.CAP_PROP_AUTO_WB, 1)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
# cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
#
#
#
#
# try:
#     while True:
#         ret, frame = cap.read()
#         if ret:
#             cv2.imshow("look", frame)
#             cv2.waitKey(24)
#
# except:
#     cap.release()
# finally:
#     cap.release()
