from Vision import *
from Communication import *
import time


queue = [] # 物块抓取顺序

# 任务一：读取二维码
def task1():
    global queue
    
    while True:
        response = recv_data()
        print("等待命令: 到达二维码区, 目前接受到: [", response, "]")
        if response is not None:
            if response == xmlReadCommand('arriveQR', 0):
                print("开始读取识别二维码")
                break
    
    # 读取二维码获取顺序
    flg = getQRCodeResult(queue)
    cmd = xmlReadCommand("qrComplete", 1)
    if flg: send_data(cmd, 0, 0) # 发送继续前进的命令

    # 显示任务信息
    pass




# 任务二：拾取物块
# 1. 对准物块，无论什么颜色
# 2. 定时抓拍，判断颜色，确定抓取
def task2():
    global queue

    # 等待小车到达原料区域
    while True:
        response = recv_data()
        print("等待命令: 到达原料区, 目前接受到: [", response, "]")
        if response is not None:
            if response == xmlReadCommand('arriveYL', 0):
                print("开始微调")
                break
    
    # 拍照用于微调，拍的时候物块不能是运动的，解决办法：等一段两倍转盘运动时间
    time.sleep(0.3)
    
    # 获取三个阈值
    color = ['red', 'green', 'blue']
    threshold = [None, None, None] # -> [[min, max], [min, max], [min, max]]
    for i, c in enumerate(color): xmlReadThreshold("item", c, threshold[i]) 

    # 进行微调
    flg = fineTuneItem(threshold)
    if not flg: return False

    # 按顺序进行抓取
    flg = catchItem(threshold, queue)
    if not flg: return False


if __name__ == '__main__':
    if not uart.isOpen(): print("串口没打开")
    pass