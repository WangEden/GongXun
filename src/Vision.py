import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
from Communication import *


def capture(dev: int, name, mode=0):
    cap = None
    if dev == 0:
        cap = cv2.VideoCapture("/dev/cameraInc")
    elif dev == 1:
        cap = cv2.VideoCapture("/dev/cameraTop")
    else:
        cap = cv2.VideoCapture("/dev/video0")
    print(cap.set(3, 640))
    cap.set(4, 480)
    cap.set(cv2.CAP_PROP_AUTO_WB, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))

    ret, frame = cap.read()
    if not ret:
        print("**摄像头打开失败**")
        return False

    if mode == 1: # 拍的时候就进行预处理
        frame = precondition(frame)

    cv2.imwrite(f"/home/pi/GongXun/src/data/{name}.jpg", frame)
    print("图片保存成功")
    cap.release()
    return True


# 获取扫码结果
def getQRCodeResult(queue: list):
    img = cv2.imread("./data/qrcode.jpg")

    if img is None:
        print("**图片读取失败**")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = decode(gray)

    if result is None or len(result) == 0:
        print("**二维码识别失败**")
        return None

    data: str = result[0].data.decode("utf-8")
    print("识别结果: ", data)

    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            queue.append(int(j))  # queue: [1, 2, 3, 3, 2, 1]


# 图像预处理
def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


# 得到二值图像连通域上外接矩形
# bbox: [box1, box2, ...]
# box: [左上角点x, 左上角点y, 宽度, 高度, ...]
def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(
        _mask, connectivity=8
    )  # connectivity参数的默认值为8
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


# 获取物块的外接矩形
def getItemRect():
    pass





# 微调物块：一两秒内需要完成
def fineTuneItem(uart):
    XCenter, YCenter = 320, 240

    img = cv2.imread("./data/yl.jpg")
    if img is None:
        return False  # 没有读到图像

    # 获取三个阈值
    Threshold = [None, None, None] # -> [[min, max], [min, max], [min, max]]
    color = ['red', 'green', 'blue']
    for i, c in enumerate(color):
        xmlReadThreshold("item", c, Threshold[i])      

    # 查找物块, 三种颜色轮流尝试, 判断依据为物块是否处于预定义的中间区域
    ROI = [XCenter-160, YCenter-160, 320, 320] # 待确定
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = None
    box = None
    # debug
    img_note = img.copy()
    n = 0 # 用于标记匹配到的颜色是哪一个
    for cth in Threshold:
        mask = cv2.inRange(img_hsv, cth[0], cth[1])
        mask = cv2.medianBlur(mask, 3)
        bbox = mask_find_b_boxs(mask)
        box = get_the_most_credible_box(bbox)
        if box is not None: # 通常不会为None
            if compRect(roi=ROI, box=box):
                break
        n+=1

    if n == 3: # 三种颜色都没匹配上, 一般不可能发生
        print("没有找到任何一个颜色")
        return False
            
    flag = True
    while flag:
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        cx = int((p1[0] + p2[0]) / 2)
        cy = int((p1[1] + p2[1]) / 2)

        udx = cx - XCenter
        udy = cy - YCenter

        k = 0
        cmd = xmlReadCommand('tweak', 1)
        dx = uDistanceToDx(udx, 16)
        dy = uDistanceToDx(udy, 16)

        # 中心偏移小于10都可以进行抓取
        if abs(udx) < 10 and abs(udy) < 10: 
            cmd = xmlReadCommand('calibrOk', 1)
            dx, dy = 0, 0
            flag = False

        print("当前要发送的命令是：", cmd, "dx, dy:", dx, dy)
        send_data(uart, cmd, dx, dy)

        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
        # cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)   
        cv2.putText(img_note, f"({udx}, {udy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.line(img_note, (320, 240), (cx, cy), (255, 0, 0), 2)
        cv2.imwrite(f"./data/img_note{k}.jpg", img_note)
        k+=1
        if flag:
            # 拍照
            if not capture(0, 'yl'): 
                return False # 拍照不成功
            img = cv2.imread("./data/yl.jpg")
            mask = cv2.inRange(img_hsv, Threshold[n][0], Threshold[n][1])
            mask = cv2.medianBlur(mask, 3)
            bbox = mask_find_b_boxs(mask)
            box = get_the_most_credible_box(bbox)
    return True


def catchItem():
    
    pass


# 判断一个矩形是否被另一个矩形包围
def compRect(roi, box):
    return (roi[0] < box[0] and roi[1] < box[1] and roi[2] > box[2] and roi[3] > box[3])


# 根据不同高度转换像素距离和实际距离
def uDistanceToDx(ud, h):
    if h == 16:
        return int(ud * 25 / 120 * 10)
    elif h == 30:
        return 0
    else:
        return 0


if __name__ == "__main__":
    print(cv2.__version__)
    capture(-1, "screen")
