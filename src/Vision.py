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


# 微调物块：一两秒内需要完成
def fineTuneItem(threshold: list, category, loop: int):
    # debug # # # # # # # # # # # # # # # # # #
    debug = 0
    with open("./logs/debug.txt", "r") as file:
        s = file.read()
        debug = int(s)
        print(f"第{debug}次测试")
    # # # # # # # # # # # # # # # # # # # # # #

    XCenter, YCenter = 320, 240
    # ROI = [XCenter-160, YCenter-160, 320, 320] # 待确定
    ROI = [0, 0, 640, 480]
    mask, box, img_note = None, None, None
    # n = 0  # 用于标记匹配到的颜色是哪一个
    AREA = 1000

    reflashScreen("正在进行微调")
    g = 0
    while True:
        if not capture(0, "yl", 0):
            print("拍照不成功")
            return False  # 拍照不成功
        img = cv2.imread("./data/yl.jpg")
        if img is None:
            return False  # 没有读到图像

        # 查找物块, 三种颜色轮流尝试, 判断依据为物块是否处于预定义的中间区域
        img = precondition(img)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.erode(img_hsv, None, iterations=2)

        if loop == 1:
            cv2.imwrite(f"./data/t21fineTuneItem/匹配时hsv{debug}_{g}.jpg", img_hsv)
        elif loop == 2:
            cv2.imwrite(f"./data/t51fineTuneItem/匹配时hsv{debug}_{g}.jpg", img_hsv)
        # debug用的一些输出图像
        img_note = img.copy()

        # 匹配颜色
        mask1 = cv2.inRange(img_hsv, threshold[0][0], threshold[0][1])
        mask2 = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
        mask3 = cv2.inRange(img_hsv, threshold[2][0], threshold[2][1])
        mask = mask1 + mask2 + mask3
        mask = cv2.medianBlur(mask, 3)

        if loop == 1:
            cv2.imwrite(f"/home/pi/GongXun/src/data/t21fineTuneItem/匹配时mask{debug}_{g}.jpg", mask)
        elif loop == 2:
            cv2.imwrite(f"/home/pi/GongXun/src/data/t51fineTuneItem/匹配时mask{debug}_{g}.jpg", mask)

        # bbox = mask_find_b_boxs(mask)
        # print(bbox)
        # bbox = sorted(bbox, key=lambda _: _[4], reverse=True)  # 按面积排
        # if len()
        # box = get_the_most_credible_box(bbox)

        bbox = mask_find_b_boxs2(mask)
        if len(bbox) == 3:

            pass
        elif len(bbox) == 2:
            pass
        elif len(bbox) == 1:
            pass
        else:
            g += 1
            continue

        if box[4] < AREA:
            print("面积太小, 不是目标")
            mask = None
            g+=1
            continue
        elif box[2] / box[3] > 1.4 or box[2] / box[3] < 0.6:
            print("比例不对, 不是目标")
            mask = None
            g+=1
            continue
        else:
            break

    # 此时 box 正好是圆形物块的外接正方形，物块的尺寸已知，box的边长已知，可以动态得到图像长度和实际距离的比值
    # 新算法得到距离比例，更准确但耗时
    # cx = int(box[0] + box[2] / 2)
    # cy = int(box[1] + box[3] / 2)
    # rectangle = np.zeros(img.shape, dtype=np.uint8)
    # rectangle = cv2.cvtColor(rectangle, cv2.COLOR_BGR2GRAY)
    # roi = rectangle.copy()
    # p1 = tuple([box[0] + 3, box[1] + 3])
    # p2 = tuple([box[0] + box[2] - 3, box[1] + box[3] - 3])
    # cv2.rectangle(rectangle, p1, p2, (255, 255, 255), 5)
    # cv2.rectangle(roi, p1, p2, (255, 255, 255), -1)
    # mask = cv2.bitwise_and(mask, mask, mask=roi)
    # points_mask = cv2.bitwise_and(mask, rectangle)
    # b_box = mask_find_b_boxs(points_mask)
    # 根据象限取点

    # 旧的算法，粗略获取距离比例
    pixel_len = (box[2] + box[3]) / 2  # box 宽高平均
    print("pixel_len:", pixel_len)
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
        dx = int(-udy * rate) # dx > 0 往东走
        dy = int(udx * rate) # dy > 0 往南走

        # 中心偏移小于8mm都可以进行抓取
        if abs(dx) < 60 and abs(dy) < 40:
            cmd = xmlReadCommand("calibrOk", 1)
            dx, dy = 0, 0
            flag = False
        else:
            print("还没调准                                         ", end="\r")

        print("当前要发送的命令是：", cmd, "udx, udy:", udx, udy, "dx, dy: (x10mm)", dx, dy)

        # for i in range(5):
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
        if loop == 1:
            cv2.imwrite(
                f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时结果{debug}+{k}.jpg", img_note
            )
        elif loop == 2:
            cv2.imwrite(
                f"/home/pi/GongXun/src/data/t51fineTuneItem/校准时结果{debug}+{k}.jpg", img_note
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

        mask = None

        # 继续捕获图像进行微调
        if flag:
            # 拍照
            if not capture(0, "yl", 1):
                return False  # 拍照不成功
            
            time.sleep(0.3)

            img = cv2.imread("./data/yl.jpg")
            if img is None:
                return False  # 图片读取不成功
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # 匹配颜色
            for cth in threshold:
                if mask is None:
                    mask = cv2.inRange(img_hsv, cth[0], cth[1])
                    mask = cv2.medianBlur(mask, 3)
                else:
                    _ = cv2.inRange(img_hsv, cth[0], cth[1])
                    mask += cv2.medianBlur(_, 3)

            # mask = cv2.inRange(img_hsv, threshold[n][0], threshold[n][1])
            # mask = cv2.medianBlur(mask, 3)
            if loop == 1:
                cv2.imwrite(
                    f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时hsv{debug}+{k}.jpg", img_hsv
                )
                cv2.imwrite(
                    f"/home/pi/GongXun/src/data/t21fineTuneItem/校准时mask{debug}+{k}.jpg", mask
                )
            elif loop == 2:
                cv2.imwrite(
                    f"/home/pi/GongXun/src/data/t51fineTuneItem/校准时hsv{debug}+{k}.jpg", img_hsv
                )
                cv2.imwrite(
                    f"/home/pi/GongXun/src/data/t51fineTuneItem/校准时mask{debug}+{k}.jpg", mask
                )
            bbox = mask_find_b_boxs(mask)
            # print(bbox)
            box = get_the_most_credible_box(bbox)
            img_note = img.copy()
            if box is not None:
                if len(box) == 0:
                    k+=1 
                    continue
            else:
                continue
            time.sleep(0.1)

    # debug # # # # # # # # # # # # # # # # # #
    with open("./logs/debug.txt", "w") as file:
        file.write(str(debug + 1))
    # # # # # # # # # # # # # # # # # # # # # #
    return True


def catchItem(threshold: list, queue: list, loop:int):
    reflashScreen("开始抓取物块")
    print("抓取顺序:", queue)
    XCenter, YCenter = 320, 240
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
        if not compRect(ROI, box) or box[2] * box[3] < 5000:
            if loop == 1:
                cv2.imwrite(f"/home/pi/GongXun/src/data/t22catchItem/不抓取原因{w}.jpg", mask)
            elif loop == 2:
                cv2.imwrite(f"/home/pi/GongXun/src/data/t52catchItem/不抓取原因{w}.jpg", mask)
            w += 1
            print("等待中, 当前颜色不匹配", box)
            continue

        # 根据颜色发不同的抓取命令
        cmd = xmlReadCommand(colorCMD[c], 1)

        print("识别到", color[c], "颜色正确, 进行抓取")
        reflashScreen(f"正在抓取{color[c]}")
        print("将发送的命令为：", cmd)
        send_data(cmd, 0, 0)
        ptr += 1

        while True:
            response = recv_data()
            print("等待抓取动作完成, 当前接收命令: [", response, "]", end='\r')
            # print("等待抓取动作完成, 当前接收命令:", response)
            if response is not None:
                if response == xmlReadCommand("mngOK", 0):
                    print("抓取动作执行完毕, 进行下一步")
                    break

        if ptr == 3:
            cmd = xmlReadCommand("task2OK", 1)  # t2ok
            print("三个物块都抓取完毕，发送:", cmd,"进行下一步")
            reflashScreen(f"物块抓取完毕")
            send_data(cmd, 0, 0)
            break


if __name__ == "__main__":
    # print(cv2.__version__)
    capture(0, "测试照片2")
