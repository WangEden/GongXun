from Communication import *
from XmlProcess import *
from Vision0 import *
# from Vision1copy import *
from Vision1 import *
from Vision2copycopy import *
from Vision3copy import *
from Vision4 import *
import time
import subprocess


sequence = [2, 1, 3, 2, 3, 1]  # 物块抓取顺序
ringRate = 1.0

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
    flg = getQRCodeResult(sequence)
    cmd = xmlReadCommand("qrComplete", 1)
    if flg:
        for i in range(2):
            send_data(cmd, 0, 0)  # 发送继续前进的命令

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


    # 获取三个物块的阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold[i])

    # 进行微调
    fineTuneItemF(threshold, category="normal", loop=1)  # 选择普通物块

    # 按顺序进行抓取
    catchItemF(threshold, sequence, loop=1)

    # 显示任务信息
    print("任务2: 第一轮原料拾取, 完成")


# 任务三：在粗加工区放置物块
# 刚开始会停在第二个色环的位置，伸出机械臂，高度保证视野中有三个色环，ps: 相邻色环之间的距离是固定的
def task3():
    global sequence, screen, ringRate

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

    reflashScreen("正在进行校准")
    # 获取距离比
    rate = getRate(1)
    ringRate = rate
    time.sleep(0.3)

    # 对准绿色色环微调
    fineTuneRing(threshold, ringRate, 1)
    time.sleep(5)

    # 根据顺序放置三个物块
    setItemBySequance(sequence, mode=0, orin=0)

    # 按顺序取回物料
    retriveBySequence(sequence)

    # 显示任务信息
    print("任务3: 第一轮粗加工, 完成")


# 任务四: 在暂存区放物料, 重复任务三部分步骤
def task4():
    global sequence, ringRate

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
    # rate = getRate2(1)
    time.sleep(0.3)

    # fineTuneRing2(threshold, rate, 1)
    fineTuneRing2(threshold, ringRate, 1)
    time.sleep(5)

    # 按顺序放置物块
    setItemBySequance(sequence, mode=0, orin=1)

    cmd = xmlReadCommand("task2OK", 1)  # t2ok
    print("暂存区放置完成，发送:", cmd,"进行下一步")
    send_data(cmd, 0, 0)

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
    # time.sleep(0.2)

    # 获取三个物块的阈值
    threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold[i])

    # 进行微调
    fineTuneItemF(threshold, category="normal", loop=2)  # 选择普通物块

    # 按顺序进行抓取
    catchItemF(threshold, sequence, loop=2)

    # 显示任务信息
    print("任务5: 第二轮原料拾取, 完成")

# 任务六: 前往粗加工区，放置第二轮物料
def task6():
    global sequence, ringRate

    reflashScreen("第二轮前往粗加工区")
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
    # reflashScreen("正在进行校准")
    # 获取距离比
    # rate = getRate()
    time.sleep(0.3)

    # 对准绿色色环微调
    # fineTuneRing(threshold, rate, 1)
    fineTuneRing(threshold, ringRate, 1)
    time.sleep(1)

    # 根据顺序放置三个物块
    # 按顺序放置物块
    setItemBySequance(sequence, mode=0, orin=0)

    # 按顺序取回物料
    retriveBySequence(sequence)

    # 显示任务信息
    print("任务6: 第二轮粗加工, 完成")


# 任务七: 前往暂存区，放置第二轮物料
def task7():
    global sequence, ringRate

    reflashScreen("第二轮前往暂存区")
    while True:
        response = recv_data()
        print("等待命令: 到达暂存区, 目前接受到: [", response, "]", end="\r")
        if response is not None:
            if response == xmlReadCommand("arriveZC", 0):
                print("开始调整")
                break
        
    # 获取三个色环阈值
    threshold1 = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("ring", c, threshold1[i])

    # 获取三个色环阈值
    threshold2 = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(["red", "green", "blue"]):
        xmlReadThreshold("item", c, threshold2[i])

    # 在暂存区校准
    fineTuneRing3(threshold1, threshold2, ringRate)

    # 按顺序放置物块
    setItemBySequance(sequence, mode=1, orin=1)

    cmd = xmlReadCommand("task2OK", 1)  # t2ok
    print("暂存区放置完成，发送:", cmd,"进行下一步")
    send_data(cmd, 0, 0)

    # 显示任务信息
    print("任务4: 第二轮暂存, 完成")


if __name__ == "__main__":
    make_print_to_file(path="./logs/")
    loader = subprocess.Popen(["/usr/bin/python3", "/home/pi/GongXun/src/Display.py"])

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    # cv2.putText(img, "213+312", (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./data/screen_template.jpg", img)

    # try:
    if not uart.isOpen():
        print("串口没打开")
    
    task1()  # 扫码
    cmd = xmlReadCommand("qrComplete", 1)
    send_data(cmd, 0, 0)  # 发送继续前进的命令
    # task2()  # 取原料
    task3()  # 粗加工

    task4()  # 暂存
    # 截取第二轮顺序
    sequence = sequence[3:]

    task5()  # 取第二轮物料
    task6()  # 第二轮粗加工
    
    task7()  # 垛码放置的暂存
    # 回启停区

    # except:
    #     loader.terminate()
    # finally:
    #     loader.terminate()
