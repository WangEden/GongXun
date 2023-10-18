from Communication import *
from XmlProcess import *
from Vision import *
from Vision2 import *
import time


sequence = [2, 1, 3]  # 物块抓取顺序
screen = np.ones((600, 1024), dtype=np.uint8) * 255


def make_print_to_file(path="./"):
    """
    path， it is a path for save your log about fuction print
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





# 任务一：读取二维码
def task1():
    global sequence, screen

    # while True:
    #     response = recv_data()
    #     print("等待命令: 到达二维码区, 目前接受到: [", response, "]", end="\r")
    #     if response is not None:
    #         if response == xmlReadCommand("arriveQR", 0):
    #             print("开始读取识别二维码")
    #             break

    # 读取二维码获取顺序
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
    global sequence, screen

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
    fineTuneItem(threshold, category="normal")  # 选择普通物块

    # 按顺序进行抓取
    catchItem(threshold, sequence)

    # 显示任务信息
    print("任务2: 原料拾取, 完成")


# 任务三：在粗加工区放置物块
# 刚开始会停在第二个色环的位置，伸出机械臂，高度保证视野中有三个色环，ps: 相邻色环之间的距离是固定的
#
def task3():
    global sequence, screen

    # 等待小车到达原料区域，并伸出机械臂
    # 小车应停在原料区绿色色环位置，之后伸出机械臂，视野范围内，必须要有至少两个色环（用于标定距离）
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

    # 计算位置, 根据顺序, 校准并放置三个物块, 按顺序抓取物块: 移动、抓取、记录位置
    orient = 0  # 0: 北, 1: 西
    mountBySequence(threshold, sequence, orient)

    #
    # catchBySequence(sequence)


def task4():
    global sequence, screen

    


if __name__ == "__main__":
    make_print_to_file(path="./")
    # cv2.namedWindow("screen", cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty("screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.imshow("screen", screen)
    # cv2.waitKey(1)

    if not uart.isOpen():
        print("串口没打开")
    # task1()
    # task2()
    task3()
