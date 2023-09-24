import sensor, image, time, ustruct, math
from pyb import UART

# 初始化串口
uart = UART(3, 115200)  # 设置串口号和波特率
uart.init(115200, bits=8, parity=None, stop=1)

#定义数据包，格式为2个帧头+4个字符数据+2个半整型数据+帧尾（11byte）
#4个字符传输命令名，2个int传输xy方向的偏差
def data_packet( a, b, c, d, i, f):
    temp = ustruct.pack(">bbbbbbhhb",
                        0x2C,      # 帧头1
                        0x3C,      # 帧头2
                        ord(str(a)), # 字符1
                        ord(str(b)), # 字符2
                        ord(str(c)), # 字符3
                        ord(str(d)), # 字符4
                        int(i), # 半整型数据1
                        int(f), # 半整型数据2
                        0x4C)      # 帧尾
    for x in range(5):
        uart.write(temp)  # 调用串口发送命令
        time.sleep_ms(100)

#声明数据包使用的全局变量
global a1,b1,c1,d1
global i1,f1 



a1,b1,c1,d1,i1,f1='a','b','c',4,125,1026

#定义数据发送函数
def send_data():
    for x in range(1):
        data_packet(a1,b1,c1,d1,i1,f1)
        time.sleep_ms(10)

#定义数据接受函数
def receive_data():
    if uart.any():  # 检查是否有数据可读取
        receive = uart.read(88)  # 从串口读取15个byte的数据 其中3-14byte为有效位
        
        if receive is not None:
            print("Received:", receive)
            time.sleep_ms(10)


while True:
    send_data()
    time.sleep_ms(1)
    receive_data()
    time.sleep_ms(1)
