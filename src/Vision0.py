import time
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
from VisionUtils import *


# 获取扫码结果
def getQRCodeResult(queue: list):
    cap = VideoCapture("/dev/cameraTop")
    while True:
        # if not capture(1, "qrcode", 0):
        #     return False  # 拍照不成功
        # img = cv2.imread("./data/qrcode.jpg")
        img = cap.read()

        if img is None:
            print("**图片读取失败**")
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = decode(gray)

        if result is None or len(result) == 0:
            print("**二维码识别失败**", end='\r')
        else:
            break
    cap.terminate()

    data: str = result[0].data.decode("utf-8")
    print("识别结果: ", data)

    img = np.ones((600, 1024), dtype=np.uint8) * 255
    cv2.putText(img, data, (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
    cv2.imwrite("./data/screen_template.jpg", img)

    queue.clear()
    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            queue.append(int(j))  # queue: [1, 2, 3, 3, 2, 1]
    return True


if __name__ == "__main__":
    pass
