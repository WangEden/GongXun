import time
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
from Communication import *
from XmlProcess import *
from VisionUtils import *


"""
任务函数：
1.扫描二维码
2.从圆盘上抓取物料
"""
# 获取扫码结果
def getQRCodeResult(queue: list):
    cameraQR = VideoCapture("/dev/cameraTop")

    c = 0
    while True:
        img = cameraQR.read()
        if img is None:
            print("**图片读取失败, 继续尝试中...**")
            if c > 15:
                return False
            c+=1
            continue

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = decode(img_gray)

        if result is None or len(result) == 0:
            print("**未发现二维码, 继续尝试中...**", end='\r')
        else:
            cameraQR.terminate() # 释放摄像头
            reflashScreen("扫描完成")
            break

    data: str = result[0].data.decode("utf-8")
    print("识别结果: ", data)

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    cv2.putText(img, data, (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./data/screen_template.jpg", img)
    
    reflashScreen(f"扫码结果为:{data}")

    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    queue.clear()
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            queue.append(int(j))  # queue: [1, 2, 3, 3, 2, 1]
    return True



