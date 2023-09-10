import serial
uart2 = serial.Serial(port="/dev/ttyAMA0", baudrate=115200)
uart2.write("Msg from UART2...".encode("gbk"))
result = None
while True:
    result = uart2.read()
    if result is not None:
        print(result)
    else:
        print("serial not data")

























