import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *


def fineTuneItemF(_threshold: list, category: str, loop: int):
    # debug # # # # # # # # # # # # # # # # # #
    debug = 0
    with open("./logs/debug.txt", "r") as file:
        s = file.read()
        debug = int(s)
        print(f"第{debug}次测试")
    # # # # # # # # # # # # # # # # # # # # # #

    # 测距离比例, 不通信 # # # # # # # # # # # # # # 
    # 设置相机参数
    cap = cv2.VideoCapture("/dev/cameraInc")
    capSet = cap.set(3, 640)
    capSet = cap.set(4, 480)
    capSet = cap.set(cv2.CAP_PROP_AUTO_WB, 1)
    capSet = cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    capSet = cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
    if (capSet):
        print("相机参数设置成功")

    # 判断圆盘是否在转动 # # # # # # # # # # # #
    ret, last_frame = cap.read()
    last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
    start_time = time.time()
    is_plate_move = True
    while is_plate_move:
        end_time = time.time()
        if (end_time - start_time > 0.1):
            start_time = time.time()
            ret, last_frame = cap.read()
        
        ret, current_frame = cap.read()
        # 圆盘没在移动时退出
        is_plate_move = moving_detect(last_frame, current_frame)
    # # # # # # # # # # # # # # # # # # # # # #

    # 计算距离比例 # # # # # # # # # # # # # # #
    XCenter, YCenter = 320, 240
    ret, frame = cap.read()
    
    img = cv2.GaussianBlur(frame, (3, 3), 0)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_hsv = cv2.erode(img_hsv, None, iterations=2)

    
    # # # # # # # # # # # # # # # # # # # # # #

    # 进行微调
    wt_count = 0
    # 判断圆盘是否在转动 # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # #


