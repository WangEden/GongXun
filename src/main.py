from Function import *
from xml.etree import ElementTree as ET
import serial
import cv2
import numpy as np


# 声明串口
uart = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=115200,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1,
)
# 参数文件
paraDomTree = ET.parse("./parameter.xml")
messageNode = paraDomTree.find("message")
ringThresholdNode = paraDomTree.find('threshold[@tag="ring"]')
itemThresholdNode = paraDomTree.find('threshold[@tag="item"]')
# 相机目录
cameraTopPath = "/dev/cameraTop"
cameraIncPath = "/dev/cameraInc"
# cameraInc = F.VideoCapture(cameraIncPath)
# cameraTop = F.VideoCapture(cameraTopPath)
# 存储物块领取顺序
catchQueue1 = []  # 第一趟 ['r', 'g', 'b']
catchQueue2 = []  # 第二趟 ['g', 'b', 'r']
# 存储阈值
redThreshold = [None, None]
greenThreshold = [None, None]
blueThreshold = [None, None]

# def start():
#     cv2.namedWindow("main")
#     cv2.resizeWindow("main", 1024, 480)
#     screen = np.ones(480, 1024) * 255
#     cv2.rectangle(screen)


def task1():  # 任务一、读取二维码
    global uart, catchQueue1, catchQueue2, cameraTopPath, messageNode

    if not uart.isOpen():
        print("Serial Not Open!")

    # 等待车已停靠在二维码旁的信号
    responce = None
    while True:
        responce = uart.read(4).decode("utf-8")
        if responce is not None:
            print("recv: ", responce)
            if responce == getMessage(messageNode, 'arrived'):
                print("succeed recv:", responce)
                print("start qrcode recognize ...")
                # 接收到到达识别二维码区域的信号
                break

    camera = VideoCapture(cameraTopPath)
    while True:
        img = camera.read()
        if img is not None:
            cv2.imshow("qrcode", img)
            cv2.waitKey(1)
            qrcode_result = getQRCodeResult(img)
            if qrcode_result is not None:
                print("qrcode result: ", qrcode_result)
                parseItemCatchQueue(qrcode_result, catchQueue1, catchQueue2)
                print("q1: ", catchQueue1, "q2: ", catchQueue2)
                cmd = getMessage(messageNode, 'qrComplete').split()
                send_data(uart, cmd, 0, 0)


def task2():  # 前往原料区、识别圆盘、校准物块、取物块
    pass


def task3():  # 前往粗加工区、识别色环颜色、校准位置、按顺序放置物块
    global uart, messageNode, cameraIncPath
    camera = VideoCapture(cameraIncPath)
    while True:
        response = uart.read(4).decode("utf-8")
        print("waiting for start wei tiao command ...")
        print("recv: ", response)
        if response == getMessage(messageNode, 'arrived'):
            print("start wei tiao ...")
            break
    
    flag = True
    while flag:
        frame = camera.read()
        if frame is None:
            print("no img !")
            continue
        # cv2.imshow("wei tiao", frame)
        # cv2.waitKey(1)
        print("processing img ...")
        img_bgr = precondition(frame)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, blueThreshold[0], blueThreshold[1])
        mask = cv2.medianBlur(mask, 3)
        bbox = mask_find_b_boxs(mask)
        img_note = frame.copy()
        most_credible_box = get_the_most_credible_box(bbox)
        if most_credible_box is not None:
            p1 = tuple([most_credible_box[0], most_credible_box[1]])
            p2 = tuple([most_credible_box[0] + most_credible_box[2], most_credible_box[1] + most_credible_box[3]])
            cx = int((p1[0] + p2[0]) / 2)
            cy = int((p1[1] + p2[1]) / 2)
            cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
            cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
            cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)
            udx = cx - XCenter
            udy = cy - YCenter
            cv2.putText(img_note, f"({udx}, {udy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
            cv2.line(img_note, (320, 240), (cx, cy), (255, 0, 0), 2)
        cv2.imshow("img_note", img_note)
        cv2.waitKey(1)
        cmd = getMessage(messageNode, 'tweak').split()
        dx = uDistanceToDx(udx, 16)
        dy = uDistanceToDx(udy, 16)
        if abs(udx) < 3 and abs(udy) < 3:
            cmd = getMessage(messageNode, 'calibrOk').split()
            dx, dy = 0, 0
            flag = False
        send_data(uart, cmd, dx, dy)
        while flag:
            response = uart.read(4).decode("utf-8")
            print("waiting for weitiao complete...")
            print("recv: ", response)
            if response == getMessage(messageNode, 'wtok'):
                print("start wei tiao ...")
                break
    print("task3 ok")

# def show_img(img):
#     cv2.imshow("hou tai img", img)
#     cv2.waitKey(24)


if __name__ == "__main__":
    getColorThreshold(itemThresholdNode, 'blue', blueThreshold)
    task3()
