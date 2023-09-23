import sensor, image, time, ustruct, math
from pyb import UART

# 初始化串口
uart = UART(3, 115200)  # 设置串口号和波特率
uart.init(115200, bits=8, parity=None, stop=1)

#定义数据包
def data_packet( a, b, c, d, e, f, g):
    temp = ustruct.pack("<bbhhhhhhhb",  # 格式为2个帧头+7个整型数据+帧尾
                        0x2C,      # 帧头1
                        0x3C,      # 帧头2
                        int(a),    # up sample by 2    #数据1
                        int(b),    # up sample by 2    #数据2
                        int(c),
                        int(d),
                        int(e),
                        int(f),
                        int(g),
                        0x4C)      # 帧尾
    for x in range(5):
        uart.write(temp);  # 调用串口发送命令
        time.sleep_ms(100)

#定义数据发送函数
def send_data(a, b, c, d, e, f, g):
    for x in range(1):
        #在此处对data进行赋值
        a=b=c=1
        d=e=f=g=2
        data_packet(a,b,c,d,e,f,g)
        time.sleep_ms(10)

#定义数据接受函数
def receive_data():
    if uart.any():  # 检查是否有数据可读取
        receive = uart.read(136)  # 从串口读取17个byte的数据 其中3-16byte为有效位
        
        if receive is not None:
            print("Received:", receive)
            time.sleep_ms(10)


while True:
    send_data()
    time.sleep_ms(1)
    receive_data()
    time.sleep_ms(1)
