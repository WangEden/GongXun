import Functions as F
import serial

# 声明串口
uart = serial.Serial(port="/dev/ttyAMA0", 
                     baudrate=115200, 
                     bytesize=8, 
                     parity=serial.PARITY_NONE, 
                     stopbits=1)


F.send_data(uart, 'Q', 'R', 'O', 'K', -21022, 156)
