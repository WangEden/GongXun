import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar


# 获取扫码结果
def getQRCodeResult(queue:list):
    img = cv2.imread('./data/qrcode.jpg')

    if img is None:
        print("**图片读取失败**")
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = decode(gray)

    if result is None or len(result) == 0:
        print("**二维码识别失败**")
        return None

    data:str = result[0].data.decode("utf-8")
    print("识别结果: ", data)

    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number: # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            queue.append(int(j)) # queue: [1, 2, 3, 3, 2, 1]


# 图像预处理
def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


# 得到二值图像连通域上外接矩形
# bbox: [box1, box2, ...]
# box: [左上角点x, 左上角点y, 宽度, 高度, ...]
def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(_mask, connectivity=8)  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


# 按照面积、位置筛选得到最可信的外接矩形
def get_the_most_credible_box(b_box):
#    global XCenter, YCenter
    XCenter = 320
    YCenter = 240
    if len(b_box) == 0:
        return None
    if len(b_box) == 1:
        return b_box[0]
    b_box = sorted(b_box, key=lambda box: abs(box[0] + box[2] / 2 - XCenter))
    # print("by dx:\n", b_box)
    b_box = sorted(b_box, key=lambda box: abs(box[1] + box[3] / 2 - YCenter))
    # print("by dy:\n", b_box)
    b_box = sorted(b_box, key=lambda box: box[4], reverse=True)
    # print("by area:\n", b_box)
    return b_box[0]
