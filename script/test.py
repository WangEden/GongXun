import serial, struct

uart = serial.Serial( # 声明串口
    port="/dev/ttyAMA0",
    baudrate=115200,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1,
    timeout=0,
    dsrdtr=True,
)

def send_data(cmd:list, i, f):
    a, b, c, d = cmd
    data = struct.pack("<bbbbbbhhb", # 四个字符作为命令, 两个浮点作为xy偏差
                        0x2C,      # 帧头1      ','
                        0x3C,      # 帧头2      '<'
                        ord(str(a)), # 字符1
                        ord(str(b)), # 字符2
                        ord(str(c)), # 字符3
                        ord(str(d)), # 字符4
                        int(i), # 半整型数据1
                        int(f), # 半整型数据2
                        0x3E)      # 帧尾       '>'
    uart.write(data)

while True:
    print("recv:", uart.read(4).decode('utf-8'))
    # send_data(['a','b','c','d'], 0, 0)