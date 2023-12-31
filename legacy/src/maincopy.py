# from Communication import *
# from XmlProcess import *
# from Vision0 import *
# from Vision1copy import *
# from Vision1 import *
# from Vision2js import *
# from Vision3copy import *
# from Vision4 import *
from VisionUtils import *
import time
import subprocess
import socket


sequence = [2, 1, 3, 2, 3, 1]  # 物块抓取顺序
ringRate = 5.18
itemRate = 3.28

# # # # # # # # # # # # # # # # # #
# # # # # # # 第 一 轮 # # # # # # #
# # # # # # # # # # # # # # # # # #

# 任务一：接收任务码
def task1():
    global sequence, screen

    # WIFI接收
    reflashScreen("准备接收任务码")
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_addr = ("", 9050)
    udp_socket.bind(local_addr)
    # while True:
    recv_data = udp_socket.recvfrom(1024)
    data = recv_data[0].decode('gbk')
    
    img = np.ones((600, 1024), dtype=np.uint8) * 255
    cv2.putText(img, data, (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./data/screen_template.jpg", img)
    print("任务1: 任务码接收, 完成, 结果为: ", sequence)

    sequence.clear()
    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            sequence.append(int(j))  # queue: [1, 2,


# 任务二：在暂存区拾取物块
# 1. 对准物块，无论什么颜色
# def task2():
#     global sequence, ringRate

#     reflashScreen("前往暂存区拾取物块取第一轮物料")
#     while True:
#         response = recv_data()
#         print("等待命令: 到达暂存区, 目前接受到: [", response, "]", end="\r")
#         if response is not None:
#             if response == xmlReadCommand("arriveZC", 0):
#                 print("到暂存区")
#                 break
        
#     # 获取三个色环阈值
#     thresholdRing = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
#     for i, c in enumerate(["red", "green", "blue"]):
#         xmlReadThreshold("ring", c, thresholdRing[i])
    
#     # 获取三个物块阈值
#     thresholdItem = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
#     for i, c in enumerate(["red", "green", "blue"]):
#         xmlReadThreshold("item", c, thresholdItem[i])
    
#     # 获取物料摆放顺序
#     rank = getItemBaiFan(thresholdItem)

#     # 在暂存区校准
#     fineTuneRing3(thresholdRing, thresholdItem, ringRate, rank)

#     # 按顺序抓取物块
#     retriveBySequence1(sequence, rank)

#     # 显示任务信息
#     print("任务2: 第一轮暂存区拾取, 完成")


# # 任务三：在精加工区放置物块和拾取物块
# # 刚开始会停在第二个色环的位置，伸出机械臂，高度保证视野中有三个色环，ps: 相邻色环之间的距离是固定的
# def task3():
#     global sequence, screen, ringRate

#     # 等待小车到达粗加工区域，并伸出机械臂
#     # 小车应停在粗加工区绿色色环位置，之后伸出机械臂，视野范围内，必须要有至少两个色环（用于标定距离）
#     reflashScreen("第一轮前往精加工区")
#     while True:
#         response = recv_data()
#         print("等待命令: 到达精加工区, 目前接受到: [", response, "]", end="\r")
#         if response is not None:
#             if response == xmlReadCommand("arriveCJ", 0):
#                 print("开始调整")
#                 break

#     # 获取三个色环阈值
#     threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
#     for i, c in enumerate(["red", "green", "blue"]):
#         xmlReadThreshold("ring", c, threshold[i])

#     # 计算位置, 校准
#     orient = 0  # 0: 北, 1: 西

#     reflashScreen("正在进行校准")
#     # 获取距离比
#     # rate = getRate(1)
#     # ringRate = rate
#     time.sleep(0.3)

#     # 对准绿色色环微调
#     fineTuneRing(threshold, ringRate, 1)
#     time.sleep(2)

#     # 根据顺序放置三个物块
#     setItemBySequance(sequence, mode=0, orin=0)

#     # 按顺序取回物料
#     retriveBySequence(sequence)

#     # 显示任务信息
#     print("任务3: 第一轮粗加工, 完成")


# # 任务四: 在圆盘放物料后回家
# def task4():
#     global sequence, ringRate

#     # 等待小车到达暂存区域，并伸出机械臂
#     # 小车应停在暂存区绿色色环位置，之后伸出机械臂，视野范围内，必须要有至少两个色环（用于标定距离）
#     reflashScreen("第一轮前往产品区")
#     while True:
#         response = recv_data()
#         print("等待命令: 到达暂存区, 目前接受到: [", response, "]", end="\r")
#         if response is not None:
#             if response == xmlReadCommand("arriveZC", 0):
#                 print("开始调整")
#                 break

#     # 获取三个物块的阈值
#     threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
#     for i, c in enumerate(["red", "green", "blue"]):
#         xmlReadThreshold("item", c, threshold[i])

#     # 进行微调
#     fineTuneItemF(threshold, category="normal", loop=1)  # 选择普通物块

#     # 按顺序进行抓取
#     setItemF(threshold, sequence, loop=1)
#     # setItemBySequance(sequence, 0, 2)

#     # 显示任务信息
#     print("任务2: 第一轮产品放置完成")


if __name__ == "__main__":
    # make_print_to_file(path="./logs/")
    loader = subprocess.Popen(["/usr/bin/python3", "/home/pi/GongXun/src/Display.py"])

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    # cv2.putText(img, "213+312", (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./data/screen_template.jpg", img)

    # try:
    # if not uart.isOpen():
    #     print("串口没打开")
    
    task1()  # 获取任务码
    # cmd = xmlReadCommand("qrComplete", 1)
    # send_data(cmd, 0, 0)  # 发送继续前进的命令
    # task2()  # 取产品
    # task3()  # 精加工
    # task4()  # 成品
    # 截取第二轮顺序
    # sequence = sequence[3:]
