import Function as F
import os
from xml.etree import ElementTree as ET
from serial import Serial
import cv2
# import numpy as np


# 声明串口
uart = Serial(port="/dev/ttyAMA0", baudrate=115200)
# 参数文件
paraDomTree = ET.parse("./parameter.xml")
message = paraDomTree.find('message')
# 相机目录
cameraTopPath = "/dev/cameraTop"
cameraIncPath = "/dev/cameraInc"
cameraTop = F.VideoCapture(cameraTopPath)
cameraInc = F.VideoCapture(cameraIncPath)


def task1(): # 任务一、读取二维码
    global uart, cameraInc
    # 等待车已停靠在二维码旁的信号
    responce = None
    while True:
        responce = uart.read()
        if responce is not None:
            if responce == message.find('arrived').text:
                # 接收到到达识别二维码区域的信号
                break
    
    img = cameraInc.read()
    qrcode_result = F.getQRCodeResult(img)
    print(qrcode_result)
    

if __name__ == "__main__":
    cv2.namedWindow("cameraInc", cv2.WINDOW_NORMAL)
    task1()
    # a = Message.find('arrived')
    # print(type(a.text))
    pass
