import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
from Communication import *


# 拍一张照片，路径存储于 ./data/<name>.jpg
# dev=0: Inc, dev=1: Top
# mode=1 进行预处理
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
    print("拍照完成, 图片保存成功")
    cap.release()
    return True


# 获取扫码结果
def getQRCodeResult(queue: list):

    while True:
        if not capture(1, 'qrcode', 0): return False # 拍照不成功
        img = cv2.imread("./data/qrcode.jpg")

        if img is None:
            print("**图片读取失败**")
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = decode(gray)

        if result is None or len(result) == 0:
            print("**二维码识别失败**")
        else:
            break

    data: str = result[0].data.decode("utf-8")
    print("识别结果: ", data)

    number = data.split("+")
    # color = {'1': 'r', '2': 'g', '3': 'b'}
    for i in number:  # number: ['123', '321']
        l = list(i)  # l : ['1', '2', '3']
        for j in l:
            queue.append(int(j))  # queue: [1, 2, 3, 3, 2, 1]
    return True


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


# 微调物块：一两秒内需要完成
def fineTuneItem(threshold: list):
    # debug # # # # # # # # # # # # # # # # # #
    debug = 0
    with open("debug.txt", "r") as file:
        s = file.read()
        debug = int(s)
        print(f"第{debug}次测试")
    # # # # # # # # # # # # # # # # # # # # # #


    XCenter, YCenter = 320, 240
    ROI = [XCenter-160, YCenter-160, 320, 320] # 待确定
    mask, box, img_note = None, None, None
    n = 0 # 用于标记匹配到的颜色是哪一个

    while True:
        if not capture(0, 'yl', 1): return False # 拍照不成功
        img = cv2.imread("./data/yl.jpg")
        if img is None: return False  # 没有读到图像

        # 查找物块, 三种颜色轮流尝试, 判断依据为物块是否处于预定义的中间区域
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.imwrite(f"./data/fineTune{debug}/img_hsv.jpg", img_hsv)


        # debug用的一些输出图像
        img_note = img.copy()

        f = True
        for cth in threshold:
            mask = cv2.inRange(img_hsv, cth[0], cth[1])
            mask = cv2.medianBlur(mask, 3)
            cv2.imwrite(f"/home/pi/GongXun/src/data/fineTune{debug}/mask.jpg", mask)
            bbox = mask_find_b_boxs(mask)
            box = get_the_most_credible_box(bbox)
            print(box)
            if box is not None: # 通常不会为None
                if compRect(roi=ROI, box=box):
                    f = False
                    break
            n+=1
        if not f: break

        if n == 3: # 三种颜色都没匹配上
            print("没有找到任何一个颜色")
            n = 0


    flag = True
    while flag:
        if not compRect(ROI, box): continue # 
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
        send_data(cmd, dx, dy)

        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
        # cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)   
        cv2.putText(img_note, f"({udx}, {udy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.line(img_note, (320, 240), (cx, cy), (255, 0, 0), 2)
        cv2.imwrite(f"/home/pi/GongXun/src/data/fineTune{debug}/img_note.jpg", img_note)
        k+=1

        while True:
            response = recv_data()
            print("等待调完信号, 当前接收: (", response, ")", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("当次微调动作完成")
                break
            

        if flag:
            # 拍照
            if not capture(0, 'yl', 1): return False # 拍照不成功
            img = cv2.imread("./data/yl.jpg")
            if img is None: return False # 图片读取不成功
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            cv2.imwrite(f"/home/pi/GongXun/src/data/fineTune{debug}/img_hsv2.jpg", img_hsv)
            mask = cv2.inRange(img_hsv, threshold[n][0], threshold[n][1])
            mask = cv2.medianBlur(mask, 3)
            cv2.imwrite(f"/home/pi/GongXun/src/data/fineTune{debug}/mask2.jpg", mask)
            bbox = mask_find_b_boxs(mask)
            box = get_the_most_credible_box(bbox)

    # debug # # # # # # # # # # # # # # # # # #
    with open("debug.txt", "w") as file:
            file.write(str(debug + 1))
    # # # # # # # # # # # # # # # # # # # # # #


    return True


def catchItem(threshold: list, queue: list):
    XCenter, YCenter = 320, 240
    ROI = [XCenter-160, YCenter-160, 320, 320] # 待确定
    color = ['红色', '绿色', '蓝色']

    mask, box, img_note = None, None, None
    ptr = 0 # 作为指针指向抓取顺序列表中的元素

    while True:
        if not capture(0, 'yl', 1): return False # 拍照不成功
        img = cv2.imread("./data/yl.jpg")
        if img is None: return False # 图片读取不成功

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


        c = queue[ptr] - 1 # ps: 1 red -> 0 redthreshold
        mask = cv2.inRange(img_hsv, threshold[c][0], threshold[c][1])
        mask = cv2.medianBlur(mask, 3)
        bbox = mask_find_b_boxs(mask)
        box = get_the_most_credible_box(bbox)
        if not compRect(ROI, box) or box[2] * box[3] < 7000:
            print("等待中, 当前颜色不匹配")
            continue

        cmd = xmlReadCommand("catch", 1)
        
        print("识别到", color[c], "颜色正确, 进行抓取")
        send_data(cmd, 0, 0)
        ptr += 1

        while True:
            response = recv_data()
            print("等待抓取动作完成, 当前接收命令:", response)
            if response is not None:
                if response == xmlReadCommand("mngOK", 0):
                    print("抓取动作执行完毕, 进行下一步")
                    break


        if ptr == 3:
            cmd = xmlReadCommand("task2OK", 1)
            print("三个物块都抓取完毕, 进行下一步")
            send_data(cmd, 0, 0)
            break


# 判断一个矩形是否被另一个矩形包围
def compRect(roi, box):
    # print("roi: ", roi, "box: ", box)
    if box is None:
        return False
    if roi[0] < box[0] and \
        roi[1] < box[1] and \
        (roi[0] + roi[2]) > (box[0] + box[2]) and \
        (roi[1] + roi[3]) > (box[1] + box[3]):
        return True
    else: 
        return False


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
