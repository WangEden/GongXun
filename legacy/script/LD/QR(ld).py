import time
import struct
import cv2
import cv2 as cv
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar

global tt

def sm():
    global tt
    tt=[]
    tp = "QR.jpg"
    img = cv2.imread(tp) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pyzbar.decode(gray)
    if result == []: 
        print("二维码识别失败")
    else:
        for i in result:
            tt=i.data.decode("utf-8") #对于result中的每个二维码数据，将其解码为UTF-8编码的字符串，并将结果赋值给tt变量
        print('二维码识别成功')
        print(tt)
        #调用并显示图像查看器查看字符串数据
        width = 400
        height = 400
        img = np.ones((height, width, 4)) * (255, 255, 255, 0) #填充为透明背景
        text = tt
        cv2.putText(img, text, (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 10)
        cv.imwrite("image.jpg", img)
        img=Image.open('image.jpg')
        img.show()
        #从tt字符串中提取所有的数字，并将结果保存在num变量中
        num = ''.join([x for x in tt if x.isdigit()]) 
        print(num)
        for i in range (0, 6) :
            z[i] = int (num) // (10 ** (5-i)) % 10            
        print(z)
        return tt

def send_data(uart, a, b, c, d, i, f):
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

sm()
'''send_data()

'''