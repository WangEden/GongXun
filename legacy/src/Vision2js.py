import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *
from collections import Counter


def fineTuneRing(threshold: list, rate: float, loop: int):

    # 微调 对准绿色色环 # # # # # # # # # # # # # # # # # # # # # # # #
    # 找出绿色色环的位置并进行微调
    # 通信部分
    # 框出色环的外接矩形最小面积
    XCenter, YCenter = xmlReadCenter()
    cap = VideoCapture("/dev/cameraInc")
    circle = None
    k=0
    flag = True
    RingLen = 50
    AREA = 7000  # 待定
    img = None
    wt_count = 0
    while flag:
        circleAll = []
        # 拍照
        # camera = VideoCapture("/dev/cameraInc")
        for i in range(15):  # 拍15张获取更准确的圆心
            img = cap.read()
            # img = cv2.GaussianBlur(img, (3, 3), 0)  # 耗时
            circleList = getCircleCenter(img)
            if len(circleList) != 0:
                for c in circleList:
                    cx, cy, r = c
                    # 将在绿色色环内的圆筛选出来
                    # if cx > box[0] and cx < box[0] + box[2] and cy > box[1] and cy < box[1] + box[3]:
                    circleAll.append((cx, cy))
            print("获取15帧图像用于处理, 当前: ", i)

        # time.sleep(0.3)

        # 找到绿色色环获取roi, 利用roi得到目标点位置
        img_note = img.copy()

        # 平滑处理, 颜色识别
        img = cv2.pyrMeanShiftFiltering(img, 15, 20)
        img = cv2.GaussianBlur(img, (3, 3), 0)

        cv2.imwrite(f"./data/t32ringwt/ceshi{k}.jpg", img)

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # img_hsv = cv2.erode(img_hsv, None, iterations=2)
        maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        maskGreen = cv2.medianBlur(maskGreen, 3)
        kernel = np.ones((3, 3), dtype=np.uint8)
        cv2.dilate(maskGreen, kernel, 3)
        cv2.imwrite(f"./data/t32ringwt/查找的绿色色环mask{k}.jpg", maskGreen)

        b_box = mask_find_b_boxs(maskGreen)
        boxs = []


        for i, v in enumerate(b_box):
            lu, lv, w, h, s = b_box[i]
            if b_box[i][4] > 800 and max(w, h) / min(w, h) < 1.5:
                boxs.append(b_box[i])
        print(boxs)
        if len(boxs) == 0:
            print("没找到色环")
            continue
        b_box = sorted(boxs, key = lambda box: box[4], reverse=True) # 找到面积最大的框
        # if len(b_box) > 1:
        #     b_box = b_box[:2]
        b_box = sorted(b_box, key = lambda box: box[0], reverse=True) # 找到面积最大的框
        # 绿色色环box

        if len(b_box) == 0:
            print("没有找到绿色色环")
            continue

        box = b_box[0]
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])

        if box[2] < RingLen and box[3] < RingLen:
            print("面积太小不符合")
            k+=1
            continue

        print(box)
        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 2)

        # debug
        for c in circleAll:
            x, y = c
            cv2.circle(img_note, (x, y), 2, (255, 0, 0), 2)

        if loop == 1:
            cv2.imwrite("./data/t32ringwt/最后一帧.jpg", img)
            cv2.imwrite(f"./data/t32ringwt/查找的绿色色环{k}.jpg", img_note)
        elif loop == 2:
            cv2.imwrite("./data/t62ringwt/最后一帧.jpg", img)
            cv2.imwrite(f"./data/t62ringwt/查找的绿色色环{k}.jpg", img_note)


        circles = []
        # 筛选出在绿色色环内的圆
        # circleAll = sorted(circleAll, key = lambda c: c[0],  reverse=True) # 包括红色 所以不能这样写
        # # 由于绿色阈值和蓝色阈值相近, 所以增加这一步筛选掉靠左的蓝色圆形, 如果有的话
        # if len(circleAll) > 15:
        #     circleAll = circleAll[:15]

        for c in circleAll:
            cu, cv = c
            if box[0] < cu < box[0] + box[2] and box[1] < cv < box[1] + box[3]:
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
            cv2.imwrite(f"./data/t32ringwt/查找的色环圆心{k}.jpg", img_note)
        elif loop == 2:
            cv2.imwrite(f"./data/t62ringwt/查找的色环圆心{k}.jpg", img_note)

        if abs(udx) < 20 and abs(udy) < 20:
            dx = 0
            dy = 0
            cmd = xmlReadCommand("calibrOk", 1)
            print("校准完成, 进行放置")
            print("将发送的命令为: ", cmd, 0, 0)
            send_data(cmd, dx, dy)
            flag = False
        else:
            if wt_count > 3:
                print("微调超出次数限制3, 强制退出")
                cmd = xmlReadCommand("calibrOk", 1)
                print("将发送的命令为: ", cmd, 0, 0)
                send_data(cmd, dx, dy)
                flag = False
            else:
                dx = int(rate * udx)  # dx > 0 往东走
                dy = int(rate * udy)
                cmd = xmlReadCommand("tweak", 1)
                print("将发送的命令为: ", cmd, dx, dy)
                send_data(cmd, dx, dy)
                wt_count += 1
        while flag:
            response = recv_data()
            print("等待微调完成的信号, 当前接收:[", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("微调动作完成")
                break
            if response == "OKOK":
                print("****************收到了OKOK*****************")
                break
        k+=1
    cap.terminate()


def setItemBySequance(queue:list, mode:int, orin: int):
    # mode: 0 普通放置, 1 码垛放置
    # orin: 0 北边 1 西边
    reflashScreen("正在进行放置")
    color = {1: 'R', 2: 'G', 3: 'B'}
    current_color = 2
    for ptr in range(3):
        # 获取将要放置的物块颜色
        targetColor = queue[ptr]
        moveX = (current_color - targetColor) * 1500  # 大于0向东走
        # # # # # # # # # # # # # # # # # # # # # # # #
        if ptr == 0:  # 针对一个bug
            if moveX != 0:  # 第一次为右移
                cmd = xmlReadCommand("moveRing", 1)
                if orin == 0: # 北 左右移动
                    send_data(cmd, 1, 0)
                elif orin == 1: # 西 上下移动
                    send_data(cmd, 0, -1)
                print("虚假移动到下一个色环中, 将发送: ", 0, -1)
                while True:
                    response = recv_data()
                    print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
                    if response == xmlReadCommand("tweakOk", 0):
                        print("虚假移动完成")
                        break
                    if response == "OKOK":
                        print("****************收到了OKOK*****************")
                        break
                cmd = xmlReadCommand("moveRingOK", 1)
                send_data(cmd, 0, 0)
                print("移动完后认为调准了, 发送: ", cmd, 0, 0)
            if moveX != 0:  # 放置虚假的卡掉真正的, 故延时
                time.sleep(2)

        # # # # # # # # # # # # # # # # # # # # # # # #
        if moveX == 0:
            # cmd = xmlReadCommand("tweak", 1)
            cmd = xmlReadCommand("calibrOk", 1)
            # send_data(cmd, 0, 0)
            print("当前要放置的颜色和下方颜色一致")
        else:
            # 执行移动
            cmd = xmlReadCommand("moveRing", 1)
            if orin == 0:
                send_data(cmd, moveX, 0)
                print("移动到下一个色环中, 将发送: ", cmd, moveX, 0)
            elif orin == 1:
                send_data(cmd, 0, -moveX)
                print("移动到下一个色环中, 将发送: ", cmd, moveX, 0)

            while True:
                response = recv_data()
                print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
                if response == xmlReadCommand("tweakOk", 0):
                    print("移动完成完成")
                    break
                if response == "OKOK":
                    print("****************收到了OKOK*****************")
                    break
            cmd = xmlReadCommand("moveRingOK", 1)
            send_data(cmd, 0, 0)
            print("移动完后认为调准了, 发送: ", cmd, 0, 0)
        time.sleep(5)
        # 执行放置
        # ff = True
        # while ff:
        if mode == 0:
            if orin == 0:  # 方向为北
                cmd = xmlReadCommand(f"set{color[targetColor]}", 1)
                send_data(cmd, 0, 0)
            elif orin == 1:  # 方向为西
                cmd = xmlReadCommand(f"dst{color[targetColor]}", 1)
                send_data(cmd, 0, 0)
        elif mode == 1:
            cmd = xmlReadCommand(f"ddset{color[targetColor]}", 1)
            send_data(cmd, 0, 0)
        print(f"放置{color[targetColor]}, 发送的命令为: ", cmd)
        while True:
            response = recv_data()
            print("等待放置动作完成的信号, 当前接收: ", response, end='\r')
            if response == xmlReadCommand("mngOK", 0):
                print("放置完成一个, 进行下一步")
                break
                # if response != "OKOK":
                #     print("没收到, 再发")
                #     time.sleep(1)
                #     continue
            current_color = targetColor
    if mode == 0:
        print("三个物块都完成放置, 准备进行取回")
    else:
        print("三个物块都完成放置, 前往原料区")
#
#
# def setItemBySequance1(queue:list, mode:int, orin: int):
#     # mode: 0 普通放置, 1 码垛放置
#     # orin: 0 北边 1 西边
#     reflashScreen("正在进行放置")
#     color = {1: 'R', 2: 'G', 3: 'B'}
#     current_color = 2
#     for ptr in range(3):
#         # 获取将要放置的物块颜色
#         targetColor = queue[ptr]
#         moveX = (current_color - targetColor) * 1500  # 大于0向东走
#         # # # # # # # # # # # # # # # # # # # # # # # #
#         if ptr == 0:  # 针对一个bug
#             if moveX != 0:  # 第一次为右移
#                 cmd = xmlReadCommand("moveRing", 1)
#                 if orin == 0: # 北 左右移动
#                     send_data(cmd, 1, 0)
#                 elif orin == 1: # 西 上下移动
#                     send_data(cmd, 0, -1)
#                 print("虚假移动到下一个色环中, 将发送: ", 0, -1)
#                 while True:
#                     response = recv_data()
#                     print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
#                     if response == xmlReadCommand("tweakOk", 0):
#                         print("虚假移动完成")
#                         break
#                     if response == "OKOK":
#                         print("****************收到了OKOK*****************")
#                         break
#                 cmd = xmlReadCommand("moveRingOK", 1)
#                 send_data(cmd, 0, 0)
#                 print("移动完后认为调准了, 发送: ", cmd, 0, 0)
#             if moveX != 0:  # 放置虚假的卡掉真正的, 故延时
#                 time.sleep(2)
#
#         # # # # # # # # # # # # # # # # # # # # # # # #
#         if moveX == 0:
#             # cmd = xmlReadCommand("tweak", 1)
#             cmd = xmlReadCommand("calibrOk", 1)
#             # send_data(cmd, 0, 0)
#             print("当前要放置的颜色和下方颜色一致")
#         else:
#             # 执行移动
#             cmd = xmlReadCommand("moveRing", 1)
#             if orin == 0:
#                 send_data(cmd, moveX, 0)
#                 print("移动到下一个色环中, 将发送: ", cmd, moveX, 0)
#             elif orin == 1:
#                 send_data(cmd, 0, -moveX)
#                 print("移动到下一个色环中, 将发送: ", cmd, moveX, 0)
#
#             while True:
#                 response = recv_data()
#                 print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
#                 if response == xmlReadCommand("tweakOk", 0):
#                     print("移动完成完成")
#                     break
#                 if response == "OKOK":
#                     print("****************收到了OKOK*****************")
#                     break
#             cmd = xmlReadCommand("moveRingOK", 1)
#             send_data(cmd, 0, 0)
#             print("移动完后认为调准了, 发送: ", cmd, 0, 0)
#         time.sleep(5)
#         # 执行放置
#         # ff = True
#         # while ff:
#         if mode == 0:
#             if orin == 0:  # 方向为北
#                 cmd = xmlReadCommand(f"set{color[targetColor]}", 1)
#                 send_data(cmd, 0, 0)
#             elif orin == 1:  # 方向为西
#                 cmd = xmlReadCommand(f"dst{color[targetColor]}", 1)
#                 send_data(cmd, 0, 0)
#         elif mode == 1:
#             cmd = xmlReadCommand(f"ddset{color[targetColor]}", 1)
#             send_data(cmd, 0, 0)
#         print(f"放置{color[targetColor]}, 发送的命令为: ", cmd)
#         while True:
#             response = recv_data()
#             print("等待放置动作完成的信号, 当前接收: ", response, end='\r')
#             if response == xmlReadCommand("mngOK", 0):
#                 print("放置完成一个, 进行下一步")
#                 break
#                 # if response != "OKOK":
#                 #     print("没收到, 再发")
#                 #     time.sleep(1)
#                 #     continue
#             current_color = targetColor
#     if mode == 0:
#         print("三个物块都完成放置, 准备进行取回")
#     else:
#         print("三个物块都完成放置, 前往原料区")
#
#
# 精加工区的取回
def retriveBySequence(queue:list):
    reflashScreen("正在取回物块")
    color = {1: 'R', 2: 'G', 3: 'B'}
    current_color = queue[2]
    for ptr in range(3):
        # 获取将要放置的物块颜色
        targetColor = queue[ptr]
        moveX = (current_color - targetColor) * 1500  # 大于0向东走
        # 执行移动
        cmd = xmlReadCommand("moveRing", 1)
        send_data(cmd, moveX, 0)
        print("移动到下一个色环中")
        while True:
            response = recv_data()
            print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("移动完成完成")
                break
            if response == "OKOK":
                print("****************收到了OKOK*****************")
                break
        cmd = xmlReadCommand("moveRingOK", 1)
        send_data(cmd, 0, 0)
        print("移动完后认为调准了, 发送: ", cmd, 0, 0)
        time.sleep(1)
        # 执行抓取
        cmd = xmlReadCommand(f"{color[targetColor]}catch", 1)
        send_data(cmd, 0, 0)
        print(f"放置{color[targetColor]}, 发送的命令为: ", cmd)
        while True:
            response = recv_data()
            print("等待放置动作完成的信号, 当前接收: ", response, end='\r')
            if response == xmlReadCommand("mngOK", 0):
                print("放置完成一个, 进行下一步")
                break
        current_color = targetColor

    cmd = xmlReadCommand("task2OK", 1)  # t2ok
    print("三个物块都回收完毕，发送:", cmd,"进行下一步前往暂存区")
    send_data(cmd, 0, 0)


def retriveBySequence1(queue:list, rank:list, orin:int):
    idxs = [1, 2, 3]
    reflashScreen("正在取回物块")
    color = {1: 'R', 2: 'G', 3: 'B'}
    # p : 1, 2, 3
    # rank : 3 1 2
    # queue: 1 3 2
    current_color = idxs[1]
    for ptr in range(3):
        # 获取将要放置的物块颜色
        targetColor = rank.index(queue[ptr]) + 1
        moveX = (current_color - targetColor) * 1500  # 大于0向东走
        # # # # # # # # # # # # # # # # # # # # # # # #
        if ptr == 0:  # 针对一个bug
            if moveX != 0:  # 第一次为右移
                cmd = xmlReadCommand("moveRing", 1)
                if orin == 0: # 北 左右移动
                    send_data(cmd, 1, 0)
                elif orin == 1: # 西 上下移动
                    send_data(cmd, 0, -1)
                print("虚假移动到下一个色环中, 将发送: ", 0, -1)
                while True:
                    response = recv_data()
                    print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
                    if response == xmlReadCommand("tweakOk", 0):
                        print("虚假移动完成")
                        break
                    if response == "OKOK":
                        print("****************收到了OKOK*****************")
                        break
                cmd = xmlReadCommand("moveRingOK", 1)
                send_data(cmd, 0, 0)
                print("移动完后认为调准了, 发送: ", cmd, 0, 0)
            if moveX != 0:  # 放置虚假的卡掉真正的, 故延时
                time.sleep(2)
        # # # # # # # # # # # # # # # # # # # # # # # #
        # 执行移动
        cmd = xmlReadCommand("moveRing", 1)
        send_data(cmd, moveX, 0)
        print("移动到下一个色环中")
        while True:
            response = recv_data()
            print("等待移动完成的信号, 当前接收:[", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("移动完成完成")
                break
            if response == "OKOK":
                print("****************收到了OKOK*****************")
                break
        cmd = xmlReadCommand("moveRingOK", 1)
        send_data(cmd, 0, 0)
        print("移动完后认为调准了, 发送: ", cmd, 0, 0)
        time.sleep(1)
        # 执行抓取
        cmd = xmlReadCommand(f"{color[targetColor]}catch", 1)
        send_data(cmd, 0, 0)
        print(f"放置{color[targetColor]}, 发送的命令为: ", cmd)
        while True:
            response = recv_data()
            print("等待放置动作完成的信号, 当前接收: ", response, end='\r')
            if response == xmlReadCommand("mngOK", 0):
                print("放置完成一个, 进行下一步")
                break
        current_color = targetColor

    cmd = xmlReadCommand("task2OK", 1)  # t2ok
    print("三个物块都回收完毕，发送:", cmd,"进行下一步前往精加工区")
    send_data(cmd, 0, 0)


if __name__ == "__main":
    pass