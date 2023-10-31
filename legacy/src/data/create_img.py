import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

img = np.ones((600, 1024), dtype=np.uint8) * 255
# cv2.putText(img, "213+312", (512 - 7 * 25, 50 + 25), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 8)
cv2.imwrite("screen_template.jpg", img)


# def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
#     if text == "":
#         return img
#     if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
#         img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#     # 创建一个可以在给定图像上绘图的对象
#     draw = ImageDraw.Draw(img)
#     # 字体的格式
#     fontStyle = ImageFont.truetype(
#         "simsun.ttc", textSize, encoding="utf-8")
#     # 绘制文本
#     draw.text(position, text, textColor, font=fontStyle, stroke_width=2)
#     # 转换回OpenCV格式
#     return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


# img = cv2AddChineseText(img, "正在回到启停区", (400, 200), (0,0,0), 60)
# cv2.imwrite("screen_template.jpg", img)

