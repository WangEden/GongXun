import time
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
from Communication import *
from XmlProcess import *
from VisionUtils import *

# # # # # # # # # # 没有问题的程序备份 10-18 # # # # # # # # # # # # 

# 获取扫码结果
def getQRCodeResult(queue: list):
    while True:
        if not capture(1, "qrcode", 0):
            return False  # 拍照不成功
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


# 微调物块：一两秒内需要完成
def fineTuneItem(threshold: list, category):
    # debug # # # # # # # # # # # # # # # # # #
    debug = 0
    with open("debug.txt", "r") as file:
        s = file.read()
        debug = int(s)
        print(f"第{debug}次测试")
    # # # # # # # # # # # # # # # # # # # # # #

    XCenter, YCenter = 320, 220
    # ROI = [XCenter-160, YCenter-160, 320, 320] # 待确定
    ROI = [0, 0, 640, 480]
    mask, box, img_note = None, None, None
    n = 0  # 用于标记匹配到的颜色是哪一个
    AREA = 700

    g = 0
    while True:
        if not capture(0, "yl", 1):
            return False  # 拍照不成功
        img = cv2.imread("./data/yl.jpg")
        if img is None:
            return False  # 没有读到图像

        # 查找物块, 三种颜色轮流尝试, 判断依据为物块是否处于预定义的中间区域
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.imwrite(f"./data/t21fineTuneItem/匹配时hsv{debug}_{g}.jpg", img_hsv)

        # debug用的一些输出图像
        img_note = img.copy()

        # 匹配颜色
        f = True
        for cth in threshold:
            mask = cv2.inRange(img_hsv, cth[0], cth[1])
            mask = cv2.medianBlur(mask, 3)
            cv2.imwrite(f"/home/pi/GongXun/src/data/t21fineTuneItem/匹配时mask{debug}_{g}.jpg", mask)
            bbox = mask_find_b_boxs(mask)
            box = get_the_most_credible_box(bbox)
            print(box)
            if box is not None:  # 通常不会为None
                if compRect(roi=ROI, box=box) and box[4] > AREA:
                    f = False
                    break
            n += 1
        if not f:
            break

        if n == 3:  # 三种颜色都没匹配上
            print("没有找到任何一个颜色")
            g+=1
            n = 0

    # 此时 box 正好是圆形物块的外接正方形，物块的尺寸已知，box的边长已知，可以动态得到图像长度和实际距离的比值
    pixel_len = (box[2] + box[3]) / 2  # box 宽高平均
    item_len = xmlReadSize(category)
    rate = item_len * 10 / pixel_len  # 将像素距离映射到实际距离的比例, 实际尺寸单位: x10mm

    # 开始校准
    flag = True
    while flag:
        if not compRect(ROI, box):
            continue  #
        p1 = tuple([box[0], box[1]])
        p2 = tuple([box[0] + box[2], box[1] + box[3]])
        cx = int((p1[0] + p2[0]) / 2)
        cy = int((p1[1] + p2[1]) / 2)

        udx = cx - XCenter
        udy = cy - YCenter

        k = 0
        cmd = xmlReadCommand("tweak", 1)
        # 图像距离转实际距离，因为抓物块时，画面相对于车头是横着的
        dx = int(-udy * rate)
        dy = int(udx * rate)

        # 中心偏移小于8mm都可以进行抓取
        if abs(dx) < 80 and abs(dx) < 80:
            cmd = xmlReadCommand("calibrOk", 1)
            dx, dy = 0, 0
            flag = False
        else:
            print("还没调准                                         ", end="\r")

        print("当前要发送的命令是：", cmd, "udx, udy:", udx, udy, "dx, dy: (x10mm)", dx, dy)
        send_data(cmd, dx, dy)

        cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
        # cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
        cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)
        cv2.putText(
            img_note,
            f"({udx}, {udy})",
            (cx, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            1,
        )
        cv2.line(img_note, (320, 240), (cx, cy), (255, 0, 0), 2)
        cv2.imwrite(
            f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时结果{debug}+{k}.jpg", img_note
        )
        k += 1

        # 发送完误差信号后等待调整动作完成
        while flag:
            response = recv_data()
            print("等待调完信号, 当前接收: (", response, ")", end="\r")
            # print(" ", end='\r')
            if response == xmlReadCommand("tweakOk", 0):
                print("\n当次微调动作完成                        ", end="\r")
                break

        # 继续捕获图像进行微调
        if flag:
            # 拍照
            if not capture(0, "yl", 1):
                return False  # 拍照不成功
            img = cv2.imread("./data/yl.jpg")
            if img is None:
                return False  # 图片读取不成功
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            cv2.imwrite(
                f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时hsv{debug}+{k}.jpg", img_hsv
            )
            mask = cv2.inRange(img_hsv, threshold[n][0], threshold[n][1])
            mask = cv2.medianBlur(mask, 3)
            cv2.imwrite(
                f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时mask{debug}+{k}.jpg", mask
            )
            bbox = mask_find_b_boxs(mask)
            box = get_the_most_credible_box(bbox)
            img_note = img.copy()
            time.sleep(0.1)

    # debug # # # # # # # # # # # # # # # # # #
    with open("debug.txt", "w") as file:
        file.write(str(debug + 1))
    # # # # # # # # # # # # # # # # # # # # # #
    return True


def catchItem(threshold: list, queue: list):
    print("抓取顺序:", queue)
    XCenter, YCenter = 320, 220
    # ROI = [XCenter - 160, YCenter - 160, 320, 320]  # 待确定
    ROI = [0, 0, 640, 480]
    color = ["红色", "绿色", "蓝色"]
    colorCMD = ["catchR", "catchG", "catchB"]

    mask, box, img_note = None, None, None
    ptr = 0  # 作为指针指向抓取顺序列表中的元素

    w = 1
    while True:
        if not capture(0, "yl", 1):
            return False  # 拍照不成功
        img = cv2.imread("./data/yl.jpg")
        if img is None:
            return False  # 图片读取不成功

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        c = queue[ptr] - 1  # ps: 1 red -> 0 redthreshold
        mask = cv2.inRange(img_hsv, threshold[c][0], threshold[c][1])
        mask = cv2.medianBlur(mask, 3)
        bbox = mask_find_b_boxs(mask)
        box = get_the_most_credible_box(bbox)
        if not compRect(ROI, box) or box[2] * box[3] < 7000:
            cv2.imwrite(f"/home/pi/GongXun/src/data/t22catchItem/不抓取原因{w}.jpg", mask)
            w += 1
            print("等待中, 当前颜色不匹配", box)
            continue

        # 根据颜色发不同的抓取命令
        cmd = xmlReadCommand(colorCMD[c], 1)

        print("识别到", color[c], "颜色正确, 进行抓取")
        print("将发送的命令为：", cmd)
        send_data(cmd, 0, 0)
        ptr += 1

        while True:
            response = recv_data()
            # print("等待抓取动作完成, 当前接收命令:", response, end='\r')
            print("等待抓取动作完成, 当前接收命令:", response)
            if response is not None:
                if response == xmlReadCommand("mngOK", 0):
                    print("抓取动作执行完毕, 进行下一步")
                    break

        if ptr == 3:
            cmd = xmlReadCommand("task2OK", 1)  # t2ok
            print("三个物块都抓取完毕，发送:", cmd,"进行下一步")
            send_data(cmd, 0, 0)
            break


if __name__ == "__main__":
    # print(cv2.__version__)
    capture(0, "测试照片2")
