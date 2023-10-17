import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *


def mountByQueue(threshold: list, queue: list, orient: int):
    XCenter, YCenter = 320, 220
    COLOR = {1: "红色", 2: "绿色", 3: "蓝色"}

    # 计算距离比
    # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # 刚开始停在红绿色环之间
    # 获取当前高度的距离比例
    # 假设视野内会看到两个色环
    # 拍10次照片以获取更准确的圆心
    circles = []
    k = 0
    cap = cv2.VideoCapture("/dev/cameraInc")
    while k < 1:
        # if not capture(0, f'sh{k}', 0): return False
        # img = cv2.imread(f'./data/sh{k}.jpg')
        ret, img = cap.read()
        if not ret:
            continue
        if img is None: 
            print(f"第{k}读取色环图片失败, 重试")
            continue
        img = precondition(img)
        circlePerList = getCircleCenter(img)
        if len(circlePerList) == 0:
            continue
        img_note = img.copy()
        for circle in circlePerList:
            cx, cy, r = circle
            cv2.circle(img_note, (cx, cy), 5, (64, 128, 256), -1)
            circles.append([cx, cy])
        cv2.imwrite(f"./data/t31ceju/算距离时采集{k}.jpg", img_note)
        # time.sleep(0.01)
        k+=1
        
    cap.release()
    result = getKmeansCenter(k=2, lis=circles) # 获取不同位置的两个点
    p1, p2 = result
    # p1, p2 = circlePerList
    p1 = tuple(np.round(p1, 0).astype(int).tolist())
    p2 = tuple(np.round(p2, 0).astype(int).tolist())
    uDistance = abs(p1[0] - p2[0])
    realDistance = 150  # 单位 mm
    rate = realDistance * 10 / uDistance  # 获取像素距离和实际距离的转换比
    
    redCx = max(p1[0], p1[0])
    curntUDis2bCX = abs(redCx - XCenter)  # 当前位置为绿色和红色色环之间
    curntDis2bCX = int(rate * curntUDis2bCX) # 当前镜头中心离红色色环的实际距离，第一次色环间切换要被减去

    # 前往、校准、放置
    # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # 要校准三次, 假设地上色环的位置颜色摆放是固定的
    currentColor = 1  # 将当前位置认定为红色色环，实际是红色色环位置偏左{curntDis2bCX}距离
    for ptr in range(3):
        targetColor = queue[ptr]

        # 前往对应色环区域
        # moveX > 0 时，向西走
        moveX = (targetColor - currentColor) * 1500 - curntDis2bCX
        cmd = xmlReadCommand("moveRing", 1)
        print("当前要发送的命令为: ", cmd, "moveX: ", moveX, 0)
        send_data(cmd, moveX, 0)
        while True:
            response = recv_data()
            print(f"等待接收到达 {COLOR[targetColor]}色环 的信号, 当前接收: [", response, "]", end='\r')
            if response == xmlReadCommand("arriveSH", 0):
                print(f"当前已到达 {COLOR[targetColor]}色环, 接下来进行微调")
                break
        
        # 微调色环
        v = 0
        wtFlag = True
        while wtFlag:
            if not capture(0, f'sh{targetColor}', 1): return False
            img = cv2.imread(f"./data/sh{targetColor}.jpg")
            if img is None: return False
            img_note = img.copy()

            circlesL = getCircleCenter(img)
            circle = get_the_most_credible_circle(circlesL)
            if circle == None:
                continue
            cx, cy, r = circle
            udx = XCenter - cx
            udy = YCenter - cy
            dx = int(udx * rate) # 大于0时，车向西走
            dy = int(udy * rate) # 大于0时，车向北走

            cv2.circle(img_note, (cx, cy), r, (64, 128, 256), 2)
            cv2.line(img_note, (XCenter, YCenter), (cx, cy), (64, 128, 256), 2)
            cv2.putText(img_note, f"({udx}, {udy})", (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (64, 128, 256), 1)
            cv2.imwrite(f"./data/t32ringwt/微调色环时{v}.jpg", img_note)
            v+=1

            cmd = xmlReadCommand("tweak", 1)
            if abs(dx) < 40 and abs(dy) < 40:
                print("当前色环的位置是准确的")
                cmd = xmlReadCommand("calibrOk", 1)
                dx, dy = 0, 0
                wtFlag = False
                
            print("当前要发送的命令为: ", cmd, "dx, dy: ", dx, dy)
            send_data(cmd, dx, dy)

            # 等待微调完成的信号
            while wtFlag:
                response = recv_data()
                print("等待校准完成的信号, 当前接收: [", response, "]", end='\r')
                if response == xmlReadCommand("tweakOk", 0):
                    print("校准动作完成, 进行下一步")
                    break

        # 放置
        time.sleep(0.3)
        CLR = {1: 'R', 2: 'G', 3: 'B'}
        cmd = xmlReadCommand(f"set{CLR[targetColor]}", 1)
        print("进行放置, 发送命令: ", cmd, 0, 0)
        send_data(cmd, 0, 0)
        while True:
            response = recv_data()
            print("等待放置动作完成的信号, 当前接收: [", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("放置动作完成, 进行下一步")
                break

        currentColor = targetColor
        curntDis2bCX = 0  # 第一次用完后就一直清零了
        # for循环结束
    
    # 三个物块都放完了, 发送信号让小车切换到下一个任务
    time.sleep(0.3)
    cmd = xmlReadCommand("set3OK", 1)
    print("将要发送的命令为: ", cmd)
    send_data(cmd, 0, 0)
    # return currentColor # 返回当前所在色环的位置


def catchByQueue(queue: list):
    # XCenter, YCenter = 320, 220
    COLOR = {1: "R", 2: "G", 3: "B"}

    crntColor = queue[2]
    for ptr in range(3):
        targetColor = queue[ptr]

        # 移动到对应的颜色区, 机械臂高度位置不变
        moveX = (targetColor - crntColor) * 1500 # moveX < 0 时向东走
        cmd = xmlReadCommand("moveRing", 1)
        print("当前要发送的命令为: ", cmd, "moveX: ", moveX, 0)
        send_data(cmd, moveX, 0)
        while True:
            response = recv_data()
            print(f"等待接收到达 {COLOR[targetColor]}色环的信号, 当前接收: [", response, "]", end='\r')
            if response == xmlReadCommand("arriveSH", 0):
                print(f"当前已到达 {COLOR[targetColor]}色环, 接下来进行抓取")
                break

        # 不微调，抓取
        time.sleep(0.3)
        cmd = xmlReadCommand(f"catch{COLOR[targetColor]}", 1)
        print("进行放置, 发送命令: ", cmd, 0, 0)
        send_data(cmd, 0, 0)
        while True:
            response = recv_data()
            print("等待抓取动作完成的信号, 当前接收: [", response, "]", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("抓取动作完成, 进行下一步")
                break
        
        crntColor = targetColor
        # for循环结束
    
    time.sleep(0.3)
    # 3个物块都回收完毕，修正光流坐标
    # 红色色环位置车的理论光流坐标为（10500, y）y根据机械臂伸出去的多少确定
    rX = 10500
    realX = rX + (crntColor - 1) * 1500
    realY = -1 # 待定
    cmd = xmlReadCommand("update", 1)
    print("将要发送的命令为: ", cmd, "修正光流坐标为: (", realX, realY, ")")
    send_data(cmd, realX, realY)



if __name__ == "__main":
    pass