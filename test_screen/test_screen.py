import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import threading


def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


class myThread(threading.Thread):
    def __init__(self, name=None):
        super(myThread, self).__init__(name=name)

    def run(self):
        print('=> Thread %s is running ...' % self.name)

thread = myThread()
thread.start()
thread.join()


cv2.namedWindow("123", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("123", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
screen = np.ones((600, 1024), dtype=np.uint8) * 255

string = "郭昕昌"
XCenter, YCenter = 320, 240
screen=cv2AddChineseText(screen, string, (XCenter, YCenter), (0, 0, 0), 60)
cv2.imshow("123", screen)
cv2.waitKey(0)

while True:
    print("asc")


