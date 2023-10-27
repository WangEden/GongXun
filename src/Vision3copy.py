import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *
from collections import Counter


"""
任务函数：
在暂存区放置物料
"""
def getRate2(loop:int):
    # 1. 最多可能出现六个色环, 通常四个，也会是两个
    # 2. 垛码放置时可能需要另外识别, 绿色色环和物块都要加入识别
    # 因为很可能之前没放绿色物块导致程序卡死, 也可以前面加个防漏取, 

    # 算两个圆心的距离比例
    img = None
    RingDis = 150
    pixelLen = 1
    rate = 1

    reflashScreen("正在进行校准")
    cap = VideoCapture("/dev/cameraInc")
    # 算距离比
    while True:
        # 读取一张照片用于算出距离比例
        # if not capture(0, 'zc', 0): return False
        # img = cv2.imread(f'./data/zc.jpg')
        img = cap.read()
        if img is None: 
            print("读取色环图片失败, 重试")
            continue
        img_note = img.copy()
        # 获取当前帧中所有的圆
        circleList = getCircleCenter(img)
        # 按从右到左排列这些圆, 得到两个色环间的像素距离
        p1, p2 = None, None
        if len(circleList) == 0:
            print("没有发现圆环, 重试")
            continue
        else:
            print("len: ", len(circleList))
            if len(circleList) > 3:
                # 先按y排序，得到台阶下的圆
                averY = 0
                for circle in circleList:
                    x, y, r = circle
                    averY += y
                averY = averY / len(circleList)
                for circle in circleList:
                    x, y, r = circle
                    if y < averY:
                        circleList.remove(circle)
                # 去除平均y以上的圆
                # circleList = sorted(circleList, key=lambda circle:circle[1], reverse=True)
                # circleList = circleList[:int(len(circleList)/2)]
            # 再按x排序，得到台阶下红色和绿色环的圆
            circleList = sorted(circleList, key=lambda circle:circle[0], reverse=True)
            # debug
            for c in circleList:
                x, y, r = c
                cv2.circle(img_note, (x, y), 2, (255, 0, 0), -1)
            p1, p2 = circleList[0], circleList[1]
            pixelLen = abs(p1[0] - p2[0])
        # 算出当前高度的距离比
        img_note = img.copy()
        cv2.line(img_note, (p1[0], p1[1]), (p2[0], p2[1]), (255, 0, 0), 2)
        rate = RingDis * 10 / pixelLen
        print("pixelLen, rate: ", pixelLen, rate)
        if loop == 1:
            cv2.imwrite(f"./data/t41ceju/描绘算距离用的线.jpg", img_note)
        elif loop == 2:
            cv2.imwrite(f"./data/t71ceju/描绘算距离用的线.jpg", img_note)
        break
    cap.terminate()
    return rate


def fineTuneRing2(threshold:list, rate: float, loop:int):
    # 进行微调对准台阶下的绿色色环
    XCenter, YCenter = xmlReadCenter()
    circle = None
    # 找出绿色色环的位置并进行微调
    # 通信部分
    cap = VideoCapture("/dev/cameraInc")
    k=0
    RingLen = 50
    flag = True
    # 框出色环的外接矩形最小面积
    AREA = 7000  # 待定
    while flag:
        circleAll = []
        # 拍照
        # camera = VideoCapture("/dev/cameraInc")
        for i in range(15):  # 拍15张获取更准确的圆心
            img = cap.read()
            # img = precondition(img) # 耗时
            circleList = getCircleCenter(img)
            if len(circleList) != 0:
                for c in circleList:
                    cx, cy, r = c
                    circleAll.append((cx, cy))
            print("获取15帧图像用于处理, 当前: ", i)

        # 找到绿色色环获取roi, 利用roi得到目标点位置
        img_note = img.copy()
        # 平滑处理, 颜色识别
        img = cv2.pyrMeanShiftFiltering(img, 15, 20)
        img = cv2.GaussianBlur(img, (3, 3), 0)

        cv2.imwrite(f"./data/t42ringwt/ceshi{k}.jpg", img)

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # img_hsv = cv2.erode(img_hsv, None, iterations=2)
        maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        maskGreen = cv2.medianBlur(maskGreen, 3)
        kernel = np.ones((3, 3), dtype=np.uint8)
        cv2.dilate(maskGreen, kernel, 1)

        cv2.imwrite(f"./data/t42ringwt/查找的绿色色环mask{k}.jpg", maskGreen)

        b_box = mask_find_b_boxs(maskGreen)
        

        boxs = []
        for i, v in enumerate(b_box):
            lu, lv, w, h, s = b_box[i]
            if b_box[i][4] > 800 and max(w, h) / min(w, h) < 1.5:
                boxs.append(b_box[i])

        print(boxs)
        if len(boxs) == 0:
            print("没有找到绿色色环")
            continue

        b_box = sorted(boxs, key = lambda box: box[4], reverse=True) # 找到面积最大的框
        # b_box = b_box[:int(len(b_box)/2)]
        b_box = sorted(b_box, key = lambda box: box[0], reverse=True)

        # 
        # 按y筛除
        # 

        # 绿色色环box
        box = b_box[0]
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        if box[2] < RingLen and box[3] < RingLen:
            print("面积太小不符合")
            k+=1
            continue

        print(box)
        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 2) 
        if loop == 1:
            cv2.imwrite("./data/t42ringwt/最后一帧.jpg", img)
            cv2.imwrite(f"./data/t42ringwt/查找的绿色色环mask{k}.jpg", maskGreen)
            cv2.imwrite(f"./data/t42ringwt/查找的绿色色环{k}.jpg", img_note)
        elif loop == 2:
            cv2.imwrite("./data/t72ringwt/最后一帧.jpg", img)
            cv2.imwrite(f"./data/742ringwt/查找的绿色色环mask{k}.jpg", maskGreen)
            cv2.imwrite(f"./data/t72ringwt/查找的绿色色环{k}.jpg", img_note)

        circles = []
        # 筛选出在绿色色环内的圆
        for c in circleAll:
            cu, cv = c
            if cu > box[0] and cu < box[0] + box[2] and cv > box[1] and cv < box[1] + box[3]:
                circles.append(c)
        # 获取绿色色环中扫描到出现最多次的圆
        circle = Counter(circles).most_common(1)  # 出现次数最多的圆心
    
        if circle == []:
            print("在绿色色环区域内没有识别到圆形")
            k+=1
            continue

        # 发送微调信号的部分
        print(circle)
        cx, cy = circle[0][0]
        udx = cx - XCenter
        udy = cy - YCenter
        cv2.circle(img_note, (cx, cy), 5, (255, 0, 0), 2)
        cv2.putText(img_note, f"py({udx}, {udy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 1)
        
        if loop == 1:
            cv2.imwrite(f"./data/t42ringwt/查找的色环圆心{k}.jpg", img_note)
        elif loop == 2:
            cv2.imwrite(f"./data/t72ringwt/查找的色环圆心{k}.jpg", img_note)
        
        if abs(udx) < 40 and abs(udy) < 75:
            dx = 0
            dy = 0
            cmd = xmlReadCommand("calibrOk", 1)
            print("校准完成, 进行放置")
            print("将发送的命令为: ", cmd, 0, 0)
            flag = False
            send_data(cmd, dx, dy)
        else:
            dx = int(rate * udy)  # dx > 0 往东走
            dy = int(-rate * udx)  # dy > 0 往南走
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