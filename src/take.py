import cv2
import numpy as np


cap = cv2.VideoCapture("/dev/cameraInc")
cap.set(3, 640)
cap.set(4, 480)
cap.set(cv2.CAP_PROP_AUTO_WB, 1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))




try:
    while True:
        ret, frame = cap.read()
        if ret:
            # cv2.imshow("look", frame)
            cv2.imwrite("take.jpg", frame)
            break
except:
    cap.release()
finally:
    cap.release()



# def capture(dev: int, name, mode=0):
#     cap = None
#     if dev == 0:
#         cap = cv2.VideoCapture("/dev/cameraInc")
#     elif dev == 1:
#         cap = cv2.VideoCapture("/dev/cameraTop")
#     else:
#         cap = cv2.VideoCapture("/dev/video0")

#     # print(cap.set(3, 640))
#     cap.set(3, 640)
#     cap.set(4, 480)
#     cap.set(cv2.CAP_PROP_AUTO_WB, 1)
#     cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
#     cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))

#     ret, frame = cap.read()
#     if not ret:
#         print("**摄像头打开失败**")
#         return False

#     if mode == 1:  # 拍的时候就进行预处理
#         frame = precondition(frame)

#     cv2.imwrite(f"/home/pi/GongXun/src/data/{name}.jpg", frame)
#     print("拍照完成, 图片保存成功")
#     cap.release()
#     return True