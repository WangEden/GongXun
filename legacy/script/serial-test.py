from Function import send_data
import serial

# 声明串口
uart = serial.Serial(port="/dev/ttyAMA0", 
                     baudrate=115200, 
                     bytesize=8, 
                     parity=serial.PARITY_NONE, 
                     stopbits=1)

send_data(uart, 'c', 't', 'm', 'd', 233, -123)
while True:
    a = uart.read(7)
    if a != None:
        print(a.decode('utf-8'))
        break