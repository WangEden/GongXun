from Vision1 import *
from Vision2js import *
from Vision4 import *
import subprocess
import socket
import numpy as np
import cv2


sequence = [2, 1, 3, 2, 3, 1]  # 默认物块抓取顺序
ringRate = 5.18
itemRate = 3.28
port = 9050


# 任务一：接收任务码
def task1():
    global sequence, port

    # WIFI接收

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2.绑定本地的相关信息，如果一个网络程序不绑定，则系统会随机分配
    local_addr = ("", 9050)
    udp_socket.bind(local_addr)

    # 3. 等待接收对方发送的数据
    recv_data = udp_socket.recvfrom(7)

    # 接收到的数据recv_data是一个元组
    # 第1个元素是对方发送的数据
    # 第2个元素是对方的ip和端口
    data = recv_data[0].decode('gbk')

    # 3.关闭套接字
    udp_socket.close()

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    cv2.putText(img, data, (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./screen_template.jpg", img)

    sequence.clear()
    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            sequence.append(int(j))
    print("任务1: 任务码接收, 完成, 结果为: ", sequence)


# 任务二: 前往暂存区
def task2():
    global sequence, ringRate

    # # 等待到暂存区 # # # # # # # # # # # # # # # # # #
    while True:
        response = recv_data()
        print("等待命令: 到达暂存区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveZC", 0):
                print("到暂存区")
                break
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # 获取色环和色块的阈值 # # # # # # # # # # # # # # # # # #
    thresholdRing = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("ring", c, thresholdRing[i])

    thresholdItem = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, thresholdItem[i])
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # 获取物料摆放顺序 # # # # # # # # # # # # # # # # # #
    rank = getItemBaiFan(thresholdItem)
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # 在暂存区校准 # # # # # # # # # # # # # # # # # #
    fineTuneItemF(thresholdItem, ringRate, rank)
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # 按顺序抓取物块 # # # # # # # # # # # # # # # # # #
    retriveBySequence1(sequence, rank)
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # 任务二完成 # # # # # # # # # # # # # # # # # #
    cmd = xmlReadCommand("task2OK", 1)
    send_data(cmd, 0, 0)
    print("发送: ", cmd)
    # # # # # # # # # # # # # # # # # # # # # # # # # #


# 任务三: 前往精加工区
def task3():
    global sequence, ringRate

    while True:
        response = recv_data()
        print("等待命令: 到达精加工区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveCJ", 0):
                print("开始调整")
                break

    # # 获取色环的阈值 # # # # # # # # # # # # # # # # # #
    thresholdRing = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("ring", c, thresholdRing[i])
    # # # # # # # # # # # # # # # # # # # # # # # # # #
    fineTuneRing(thresholdRing, ringRate, 1)
    time.sleep(5)

    # 根据顺序放置三个物块
    setItemBySequance(sequence, mode=0, orin=0)

    # 按顺序取回物料
    retriveBySequence(sequence)

    cmd = xmlReadCommand("task2OK", 1)
    send_data(cmd, 0, 0)
    print("发送: ", cmd)
#
#
# 任务四: 前往成品区
# def task4():
#     global sequence, itemRate
#
#
#     cmd = xmlReadCommand("task2OK", 1)
#     send_data(cmd, 0, 0)
#     print("发送: ", cmd)


if __name__ == "__main__":
    loader = subprocess.Popen(["/usr/bin/python3", "./Display.py"])

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    cv2.imwrite("./screen.jpg", img)
    cv2.imwrite("./screen_template.jpg", img)

    reflashScreen("准备接收任务码")
    task1()  # 获取任务码

    reflashScreen("前往暂存区")
    task2()

    reflashScreen("前往精加工区")
    task3()

    time.sleep(30)
    reflashScreen("前往成品区")
    # task4()
    #
    # reflashScreen("回到启停区")

    while True:
        pass


