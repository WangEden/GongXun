import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

flag = True


def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "./data/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def handler(event, x, y, flags, param):
    global flag
    if x > 900 and x < 980 and y > 60 and y < 100:
        flag = False    


if __name__ == "__main__":
    cv2.namedWindow("screen", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("screen", handler)
    # print("子程序运行中...")
    while flag:
        screen = cv2.imread("./data/screen.jpg")
        cv2.rectangle(screen, (900, 60), (980, 100), (255, 255, 255), 2)
        screen = cv2AddChineseText(screen, "关闭", (900, 60), (255, 255, 255), 40)
        cv2.imshow("screen", screen)
        cv2.waitKey(1000)
