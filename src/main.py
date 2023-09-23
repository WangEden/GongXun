import Function as F
import os
from xml.etree import ElementTree as ET
import serial
import cv2
# import numpy as np


# 声明串口
uart = serial.Serial(port="/dev/ttyAMA0", 
                     baudrate=115200, 
                     bytesize=8, 
                     parity=serial.PARITY_NONE, 
                     stopbits=1)
# 参数文件
paraDomTree = ET.parse("./parameter.xml")
message = paraDomTree.find('message')
# 相机目录
cameraTopPath = "/dev/cameraTop"
cameraIncPath = "/dev/cameraInc"
cameraInc = F.VideoCapture(cameraIncPath)
cameraTop = F.VideoCapture(cameraTopPath)
# 存储物块领取顺序
catchQueue1 = [] # 第一趟
catchQueue2 = [] # 第二趟


def task1(): # 任务一、读取二维码
    global uart, cameraInc, catchQueue1, catchQueue2
    if not uart.isOpen():
        print("Serial Not Open!")
    # 等待车已停靠在二维码旁的信号
    responce = None
    # print("wish: ", message.find('arrived').text)
    while True:
        responce = uart.read(2).decode('utf-8')
        if responce is not None:
            # print("recv: ", responce)
            if responce == message.find('arrived').text:
                print("succeed:", responce)
                # 接收到到达识别二维码区域的信号
                break
        # print("lloop")
    
    while True:
        img = cameraInc.read()
        # print(img)
        # cv2.imshow("cameraInc", img)
        cv2.waitKey(24)
        qrcode_result = F.getQRCodeResult(img)
        if qrcode_result is not None:
            print(qrcode_result)
            F.parseItemCatchQueuese(qrcode_result, catchQueue1, catchQueue2)
            print("q1: ", catchQueue1, "q2: ", catchQueue2)
            uart.write("QROK".encode("gbk"))


def task2(): # 前往原料区、识别圆盘、校准物块、取物块
    pass


def task3(): # 前往粗加工区、识别色环
    pass


if __name__ == "__main__":
    cv2.namedWindow("cameraInc", cv2.WINDOW_NORMAL)
    task1()
