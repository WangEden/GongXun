import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *
from collections import Counter


"""
任务函数：
在暂存区垛码放置物料
"""
def fineTuneRing3(thresholdRing:list, thresholdItem:list, ringRate:float, rank:list):

    # 1. 最多可能出现六个色环, 通常四个，也会是两个
    # 2. 垛码放置时可能需要另外识别, 绿色色环和物块都要加入识别
    # 因为很可能之前没放绿色物块导致程序卡死, 也可以前面加个防漏取, 
    # 进行微调对准台阶下的绿色色环
    XCenter, YCenter = xmlReadCenter()
    cap = VideoCapture("/dev/cameraInc")
    circle = None
    # 找出绿色色环的位置并进行微调
    # 通信部分
    k=0
    flag = True
    RingLen = 50
    # 框出色环的外接矩形最小面积
    AREA = 7000  # 待定
    while flag:
        img = cap.read()
        # 找到绿色色环获取roi, 利用roi得到目标点位置
        img_note = img.copy()
        # 平滑处理, 颜色识别
        img = cv2.pyrMeanShiftFiltering(img, 15, 20)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.erode(img_hsv, None, iterations=2)
        # maskGreenRing = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        # maskGreenRing = cv2.medianBlur(maskGreenRing, 3)
        # kernel = np.ones((3, 3), dtype=np.uint8)
        # cv2.dilate(maskGreenRing, kernel, 1)
        maskCenter = cv2.inRange(img_hsv, thresholdItem[rank[1]][0], thresholdItem[rank[1]][1])
        maskCenter = cv2.medianBlur(maskCenter, 3)

        b_box = mask_find_b_boxs(maskCenter)
        boxs = []

        for i, v in enumerate(b_box):
            lu, lv, w, h, s = b_box[i]
            if b_box[i][4] > 800 and max(w, h) / min(w, h) < 1.5:
                boxs.append(b_box[i])

        b_box = sorted(b_box, key = lambda box: box[4], reverse=True) # 找到面积最大的框
        # b_box = b_box[:int(len(b_box)/2)]
        b_box = sorted(b_box, key = lambda box: box[1], reverse=True)
        
        if len(b_box) == 0:
            print("没有找到中间的物块")
            continue

        # 绿色色环box
        box = b_box[0]
        lu, lv, w, h, s = box
        pru = tuple([lu + w, lv])
        pld = tuple([lu, lv + h])
        pc = tuple([lu + int(w / 2), lv + int(h / 2)])
        udx, udy = pc[0] - XCenter, pc[1] - YCenter
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        if box[2] < RingLen and box[3] < RingLen:
            print("面积太小不符合")
            k+=1
            continue

        print(box)
        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 2) 
        
        if abs(udx) < 25 and abs(udy) < 25:
            dx = 0
            dy = 0
            cmd = xmlReadCommand("calibrOk", 1)
            print("校准完成, 进行放置")
            print("将发送的命令为: ", cmd, 0, 0)
            flag = False
            send_data(cmd, dx, dy)
        else:
            dx = int(ringRate * udy)  # dx > 0 往东走
            dy = int(-ringRate * udx)  # dy > 0 往南走
            cmd = xmlReadCommand("tweak", 1)
            print("将发送的命令为: ", cmd, dy, dx)
            send_data(cmd, dx, dy)

        while flag:
            response = recv_data()
            print("等待微调完成的信号, 当前接收:[", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("微调动作完成")
                break
        k+=1
    cap.terminate()


if __name__ == "__main__":
    pass