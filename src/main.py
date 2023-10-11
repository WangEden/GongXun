from Function import *
from xml.etree import ElementTree as ET
import serial
import cv2
import numpy as np


# 声明串口 
"""
port：设备名称或None。如COM1,COM2,COM3,COM4......如果port设置为0对应的为COM1。
baudrate（int）：设置波特率，如9600或115200等。
bytesize：数据位，可能的值：FIVEBITS、SIXBITS、SEVENBITS、EIGHTBITS。
parity：奇偶校验， 启用奇偶校验。PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE。
stopbits：停止位，可能的值：STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO。
timeout（float）：设置读取超时值，timeout = None: 长时间等待；timeout = 0: 不阻塞形式 (读完之后就返回)；timeout = x: x秒后超时 (float allowed)。
xonxoff（bool）：启用软件流控制。
rtscts（bool）：启用硬件（RTS / CTS）流量控制。
dsrdtr（bool）：启用硬件（DSR / DTR）流控制。
write_timeout（float）：设置写超时值。
inter_byte_timeout（float）：字符间超时，None禁用（默认）。
"""
uart = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=115200,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1,timeout=0,dsrdtr=True
)
# 参数文件
paraDomTree = ET.parse("./parameter.xml")
messageNode = paraDomTree.find("message")
ringThresholdNode = paraDomTree.find('threshold[@tag="ring"]')
itemThresholdNode = paraDomTree.find('threshold[@tag="item"]')
# 相机目录
cameraTopPath = "/dev/cameraTop"
cameraIncPath = "/dev/video0"
# cameraInc = F.VideoCapture(cameraIncPath)
# cameraTop = F.VideoCapture(cameraTopPath)
# 存储物块领取顺序
catchQueue1 = []  # 第一趟 ['r', 'g', 'b']
catchQueue2 = []  # 第二趟 ['g', 'b', 'r']
# 存储阈值
redThreshold = [None, None]
greenThreshold = [None, None]
blueThreshold = [None, None]
XCenter = 320
YCenter = 240

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
    global uart, messageNode, cameraIncPath
    camera = VideoCapture(cameraIncPath)
    print("start task2")
    while True:
        response = uart.read(4).decode("utf-8")
        print("wait kswt command & recv: [", response, "]")
        if response is None:
            continue
        if response == getMessage(messageNode, 'arriveYL', 0):
            print("start wei tiao ...")
            break
    
    flag = True
    while flag:
        frame = camera.read()
        if frame is None:
            print("no img !")
            continue
        print("prepare img ...")
        cv2.imshow("wei tiao", frame)
        cv2.waitKey(1)
        
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
        
        cmd = getMessage(messageNode, 'tweak', 1)
        dx = uDistanceToDx(udx, 16)
        dy = uDistanceToDx(udy, 16)
        if abs(udx) < 3 and abs(udy) < 3:
            cmd = getMessage(messageNode, 'calibrOk', 1)
            dx, dy = 0, 0
            flag = False
        print(cmd)
        print("dx, dy: ", dx, dy)
        send_data(uart, cmd, dx, dy)
        
        while flag:
            response = uart.read(4).decode("utf-8")
            print("waiting weitiao action complete & recv: [", response, "]")
            if response is None:
                continue
            if response == getMessage(messageNode, 'wtok', 0):
                print("start wei tiao ...")
                break
    print("task2 ok")


def task3():  # 前往粗加工区、识别色环颜色、校准位置、按顺序放置物块
    pass

# def show_img(img):
#     cv2.imshow("hou tai img", img)
#     cv2.waitKey(24)


if __name__ == "__main__":
    getColorThreshold(itemThresholdNode, 'blue', blueThreshold)
    task2()
