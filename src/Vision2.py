import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *
from collections import Counter


def mountBySequence(threshold: list, queue: list, orient: int):
    XCenter, YCenter = 320, 220
    COLOR = {1: "红色", 2: "绿色", 3: "蓝色"}

    # 方法二：用两个圆心算距离比

    # 找到绿色色环
    img = None
    k=0
    Ringlen = 150 # mm 待定
    while True:
        AREA = 7000  # 待定
        if not capture(0, 'sh', 1): return False
        img = cv2.imread(f'./data/sh.jpg')
        if img is None: 
            print("读取色环图片失败, 重试")
            continue 

        circleList = getCircleCenter(img)
        pixelLen = 1
        if len(circleList) == 0:
            print("没有发现圆环, 重试")
            continue
        elif len(circleList) == 2:
            p1, p2 = circleList
            pixelLen = abs(p1[0] - p2[0])
        elif len(circleList) == 3:
            sorted(circleList, key=lambda circle:circle[0], reverse=True)
            p1, p2 = circleList[0], circleList[1]
            pixelLen = abs(p1[0] - p2[0])

        img = precondition(img)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        img_note = img.copy()
        maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        kernel = np.ones((3, 3), dtype=np.uint8)
        cv2.dilate(maskGreen, kernel, 1) 
        cv2.imwrite(f"./data/t31ceju/查找绿色色环mask{k}.jpg", maskGreen)
        b_box = mask_find_b_boxs(maskGreen)
        b_box = sorted(b_box, key = lambda box: box[4], reverse=True) # 找到面积最大的框
        
        if len(b_box) == 0:
            print("没有找到绿色色环")
            continue
        
        box = b_box[0]
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        
        cv2.rectangle(img_note, p1, p2, (255, 255, 255), 2)
        print(box)
        cv2.imwrite(f"./data/t31ceju/查找绿色色环{k}.jpg", img_note)
        if box[2] * box[3] < AREA:
            print("面积太小不符合")
            k+=1
            continue

        rate = Ringlen * 10 / pixelLen
        print("rate: ", rate)

        c = None
        for circle in circleList:
            cu, cv, r = circle
            if cu > box[0] and cu < box[0] + box[2] and cv > box[1] and cv < box[1] + box[3]:
                c = circle
                break
        
        if c == None:
            print("在绿色色环区域内没有识别到圆形")
            k+=1
            continue

        cu, cv, r = c
        moveU = cu - XCenter
        moveXY = 0
        cv2.circle(img_note, (cu, cv), 4, (255, 0, 0), -1)
        cv2.putText(img_note, f"moveU: {moveU}", (cu, cv), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.imwrite(f"./data/t31ceju/绿色色环圆点位置{k}.jpg", img_note)

        cmd = xmlReadCommand("moveRing", 1)
        if orient == 0:  # 车头朝北
            moveXY = int(rate * moveU)  # move > 0 往东走
            print("将发送的命令为: ", cmd, moveXY, 0)
            send_data(cmd, moveXY, 0)
        elif orient == 1: # 车头朝西
            moveXY = int(-rate * moveU)  # move > 0 往南走
            print("将发送的命令为: ", cmd, 0, moveXY)
            send_data(cmd, 0, moveXY)
        break        
        # 之后机械臂下放

    while True:
        response = recv_data()
        print("等待车到达绿色色环前方, 并下放机械臂的信号, 当前接收: ", response, end='\r')
        if response == xmlReadCommand("arriveSH", 0):
            print("车已位于绿色色环前方")
            break

    # 微调对准绿色色环
    k = 0
    rate = 1
    # 重新测距
    while True:
        AREA = 14000
        if not capture(0, 'sh', 1): return False
        img = cv2.imread(f'./data/sh.jpg')
        if img is None: 
            print("读取色环图片失败, 重试")
            continue

        circleList = getCircleCenter(img)
        if len(circleList) == 0:
            print("没有发现圆环, 重试")
            continue

        img = precondition(img)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        img_note = img.copy()
        maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        b_box = mask_find_b_boxs(maskGreen)
        b_box = sorted(b_box, key=lambda box: box[4], reverse=True) # 找到面积最大的框
        
        box = b_box[0]
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        print(box)
        
        cv2.rectangle(img_note, p1, p2, (255, 255, 255), 2)
        cv2.imwrite(f"./data/t32ringwt/微调{k}.jpg", img_note)
        if box[2] * box[3] < AREA:
            print("面积太小不符合")
            k+=1
            continue

        rate = Ringlen * 10 / max(box[2], box[3])
        break

    # 微调
    camera = VideoCapture("/dev/cameraInc")
    flag = True
    while flag:
        circles = []
        for i in range(15):  # 拍15张获取更准确的圆心
            img = camera.read()
            img = precondition(img)
            circleList = getCircleCenter(img)
            if len(circleList) != 0:
                for c in circleList:
                    cx, cy, r = c
                    circles.append((cx, cy))
        circle = Counter(circles).most_common(1)  # 出现次数最多的圆心
        cx, cy = circles
        udx = cx - XCenter
        udy = cy - YCenter
        cmd = xmlReadCommand("tweak", 1)
        dx, dy = 0, 0
        if orient == 0:  # 车头朝北
            dx = int(rate * udx)  # move > 0 往东走
            dy = int(rate * udy)
            print("将发送的命令为: ", cmd, dx, dy)
        elif orient == 1:  # 车头朝西
            dx = int(-rate * udy)  # move > 0 往南走
            dy = int(rate * udx)
            print("将发送的命令为: ", cmd, dy, dx)
        if abs(udx) < 40 and abs(udy) < 40:
            dx = 0
            dy = 0
            cmd = xmlReadCommand("calibrOk", 1)
            flag = False
        send_data(cmd, dx, dy)
        print("校准完成, 进行放置")

    # 放置
    for i in range(3):
        c = queue[i]
        color = {1: 'R', 2: 'G', 3: 'B'}
        cmd = xmlReadCommand(f"set{color[c]}", 1)
        send_data(cmd, 0, 0)
        while True:
            response = recv_data()
            print("等待放置动作完成的信号, 当前接收: ", response, end='\r')
            if response == xmlReadCommand("mngOK", 0):
                print("放置完成一个, 进行下一步")
                break
    print("三个物块都完成放置, 进行下一步, 抓取")
    # 抓取
    for i in range(3):
        c = queue[i]
        color = {1: 'R', 2: 'G', 3: 'B'}
        cmd = xmlReadCommand(f"catch{color[c]}", 1)
        send_data(cmd, 0, 0)
        while True:
            response = recv_data()
            print("等待抓取动作完成的信号, 当前接收: ", response, end='\r')
            if response == xmlReadCommand("mngOK", 0):
                print("抓取完成一个, 进行下一步")
                break
    print("进行下一个任务")
    cmd = xmlReadCommand("task3OK", 1)
    send_data(cmd, 0, 0)


# def catchBySequence(queue: list):
#     # XCenter, YCenter = 320, 220
#     COLOR = {1: "R", 2: "G", 3: "B"}
#
#     crntColor = queue[2]
#     for ptr in range(3):
#         targetColor = queue[ptr]
#
#         # 移动到对应的颜色区, 机械臂高度位置不变
#         moveX = (targetColor - crntColor) * 1500 # moveX < 0 时向东走
#         cmd = xmlReadCommand("moveRing", 1)
#         print("当前要发送的命令为: ", cmd, "moveX: ", moveX, 0)
#         send_data(cmd, moveX, 0)
#         while True:
#             response = recv_data()
#             print(f"等待接收到达 {COLOR[targetColor]}色环的信号, 当前接收: [", response, "]", end='\r')
#             if response == xmlReadCommand("arriveSH", 0):
#                 print(f"当前已到达 {COLOR[targetColor]}色环, 接下来进行抓取")
#                 break
#
#         # 不微调，抓取
#         time.sleep(0.3)
#         cmd = xmlReadCommand(f"catch{COLOR[targetColor]}", 1)
#         print("进行放置, 发送命令: ", cmd, 0, 0)
#         send_data(cmd, 0, 0)
#         while True:
#             response = recv_data()
#             print("等待抓取动作完成的信号, 当前接收: [", response, "]", end='\r')
#             if response == xmlReadCommand("tweakOk", 0):
#                 print("抓取动作完成, 进行下一步")
#                 break
#
#         crntColor = targetColor
#         # for循环结束
#
#     time.sleep(0.3)
#     # 3个物块都回收完毕，修正光流坐标
#     # 红色色环位置车的理论光流坐标为（10500, y）y根据机械臂伸出去的多少确定
#     rX = 10500
#     realX = rX + (crntColor - 1) * 1500
#     realY = -1 # 待定
#     cmd = xmlReadCommand("update", 1)
#     print("将要发送的命令为: ", cmd, "修正光流坐标为: (", realX, realY, ")")
#     send_data(cmd, realX, realY)



if __name__ == "__main":
    pass