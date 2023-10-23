from Communication import *
from XmlProcess import *
from Vision import *
from Vision2 import *
from Vision3 import *
import time
import subprocess


sequence = [2, 1, 3, 2, 3, 1]  # 物块抓取顺序


# 用于创建日志文件
def make_print_to_file(path="./"):
    """
    path, it is a path for save your log about fuction print
    example:
    use  make_print_to_file()   and the   all the information of funtion print , will be write in to a log file
    :return:
    """
    import sys
    import os
    import sys
    import datetime

    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            self.terminal = sys.stdout
            self.path = os.path.join(path, filename)
            self.log = open(
                self.path,
                "a",
                encoding="utf8",
            )
            self.count = 0
            self.last_message = ""
            print("save:", os.path.join(self.path, filename))

        def write(self, message):
            # 限制重复日志内容写入次数
            self.terminal.write(message)
            if self.last_message == message:
                self.count+=1
            else:
                self.count = 0
                self.last_message = message
            if self.count < 10:
                self.log.write(message)

        def flush(self):
            pass

    fileName = datetime.datetime.now().strftime("day" + "%Y_%m_%d_%H_%M")
    sys.stdout = Logger(fileName + ".log", path=path)

    print(fileName.center(60, "*"))


# # # # # # # # # # # # # # # # # #
# # # # # # # 第 一 轮 # # # # # # #
# # # # # # # # # # # # # # # # # #

# 任务一：读取二维码
def task1():
    global sequence, screen

    # 等待启动信号
    # while True:
    #     response = recv_data()
    #     print("等待命令: 启动系统, 目前接受到: [", response, "]", end="\r")
    #     if response is not None:
    #         if response == xmlReadCommand("arriveQR", 0):
    #             print("系统启动")
    #             break

    # 读取二维码获取顺序
    reflashScreen("准备扫码")
    getQRCodeResult(sequence)
    # cmd = xmlReadCommand("qrComplete", 1)
    # if flg:
        # send_data(cmd, 0, 0)  # 发送继续前进的命令

    # 显示任务信息
    print("任务1: 二维码读取, 完成, 结果为: ", sequence)


# 任务二：拾取物块
# 1. 对准物块，无论什么颜色
# 2. 定时抓拍，判断颜色，确定抓取
def task2():
    global sequence

    reflashScreen("前往原料区取第一轮物料")
    # 等待小车到达原料区域
    while True:
        response = recv_data()
        print("等待命令: 到达原料区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveYL", 0):
                print("开始微调")
                break

    # 拍照用于微调，拍的时候物块不能是运动的，解决办法：等一段两倍转盘运动时间
    time.sleep(0.2)

    # 获取三个物块的阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold[i])

    # 进行微调
    fineTuneItem(threshold, category="normal", loop=1)  # 选择普通物块

    # 按顺序进行抓取
    catchItem(threshold, sequence, loop=1)

    # 显示任务信息
    print("任务2: 第一轮原料拾取, 完成")


# 任务三：在粗加工区放置物块
# 刚开始会停在第二个色环的位置，伸出机械臂，高度保证视野中有三个色环，ps: 相邻色环之间的距离是固定的
#
def task3():
    global sequence, screen

    # 等待小车到达粗加工区域，并伸出机械臂
    # 小车应停在粗加工区绿色色环位置，之后伸出机械臂，视野范围内，必须要有至少两个色环（用于标定距离）
    reflashScreen("第一轮前往粗加工区")
    while True:
        response = recv_data()
        print("等待命令: 到达粗加工区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveCJ", 0):
                print("开始调整")
                break

    # 获取三个色环阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("ring", c, threshold[i])

    # 计算位置, 校准
    orient = 0  # 0: 北, 1: 西
    fineTuneRing(threshold, 1)

    # 根据顺序放置三个物块
    setItemBySequance(sequence, 0)

    # 按顺序取回物料
    retriveBySequence(sequence)

    # 显示任务信息
    print("任务3: 第一轮粗加工, 完成")


# 任务四: 在暂存区放物料, 重复任务三部分步骤
def task4():
    global sequence

    # 等待小车到达暂存区域，并伸出机械臂
    # 小车应停在暂存区绿色色环位置，之后伸出机械臂，视野范围内，必须要有至少两个色环（用于标定距离）
    reflashScreen("第一轮前往暂存区")
    while True:
        response = recv_data()
        print("等待命令: 到达暂存区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveZC", 0):
                print("开始调整")
                break
        
    # 获取三个色环阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("ring", c, threshold[i])

    # 在暂存区校准
    fineTuneRing2(threshold, 1)

    # 按顺序放置物块
    setItemBySequance(sequence, 0)

    # 显示任务信息
    print("任务4: 第一轮暂存, 完成")

# # # # # # # # # # # # # # # # # #
# # # # # # # 第 二 轮 # # # # # # #
# # # # # # # # # # # # # # # # # #

# 任务五: 回到原料区, 取第二轮物料
def task5():
    global sequence

    reflashScreen("回到原料区取第二轮物料")
    # 等待小车到达原料区域
    while True:
        response = recv_data()
        print("等待命令: 到达原料区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveYL", 0):
                print("开始微调")
                break

    # 拍照用于微调，拍的时候物块不能是运动的，解决办法：等一段两倍转盘运动时间
    time.sleep(0.2)

    # 获取三个物块的阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold[i])

    # 进行微调
    fineTuneItem(threshold, category="normal", loop=2)  # 选择普通物块

    # 按顺序进行抓取
    catchItem(threshold, sequence, loop=2)

    # 显示任务信息
    print("任务5: 第二轮原料拾取, 完成")


# 任务六: 前往粗加工区，放置第二轮物料
def task6():
    global sequence


# 任务七: 前往暂存区，放置第二轮物料
def task7():
    global sequence


if __name__ == "__main__":
    make_print_to_file(path="./logs/")
    loader = subprocess.Popen(["/usr/bin/python3", "/home/pi/GongXun/src/Display.py"])

    try:
        if not uart.isOpen():
            print("串口没打开")
        
        # task1()  # 扫码
        # task2()  # 取原料
        task3()  # 粗加工

        # 截取第二轮顺序
        sequence = sequence[3:]
        task4()  # 暂存

        # task5()  # 取第二轮物料
        # task6()  # 第二轮粗加工
        
        # task7()  # 垛码放置的暂存
        # 回启停区



    except:
        loader.terminate()
    finally:
        loader.terminate()
