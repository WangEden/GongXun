from Vision import *
from Communication import *
import time


uart = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=115200,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1,
    timeout=0,
    dsrdtr=True,
)

# 任务一：读取二维码
def task1():
    pass


# 任务二：拾取物块
# 1. 对准物块，无论什么颜色
# 2. 定时抓拍，判断颜色，确定抓取
def task2():
    global uart
    # 等待小车到达原料区域
    while True:
        response = uart.read(4).decode('utf-8')
        print("等待命令kstz, 目前接受到: [", response, "]")
        if response is None:
            continue
        if response == xmlReadCommand('tweak', 0):
            print("开始微调")
            break
    
    # flag = True
    # while flag:
    # 拍照用于微调，拍的时候物块不能是运动的，解决办法：等一段两倍转盘运动时间
    time.sleep(0.3)
    
    # 进行微调
    flg = fineTuneItem(uart)
    if flg:
        flg = catchItem()
    



if __name__ == '__main__':
    pass