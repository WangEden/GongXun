import time
import numpy as np
import cv2
from Communication import *
from XmlProcess import *
from VisionUtils import *


# 获取物料摆放顺序
def getItemBaiFan(thresholdItem: list):
    flag = True
    # 读取一张照片
    if not capture(0, 'zc', 0): return False
    img = cv2.imread(f'./data/zc.jpg')

    img = cv2.GaussianBlur(img, (3, 3), 0)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_hsv = cv2.erode(img_hsv, None, iterations=2)

    l = []
    # 获取红色位置
    mask = cv2.inRange(img_hsv, thresholdItem[0][0], thresholdItem[0][1])
    mask = cv2.medianBlur(mask, 3)
    b_box = mask_find_b_boxs(mask)
    if len(b_box) == 0:
        flag = False
    b_boxR = sorted(b_box, key=lambda box: box[4], reverse=True)  # 获取面积最大
    if flag:
        boxR = b_boxR[0]
        xR = boxR[0]
        l.append(xR)

    # 获取绿色位置
    mask = cv2.inRange(img_hsv, thresholdItem[1][0], thresholdItem[1][1])
    mask = cv2.medianBlur(mask, 3)
    b_box = mask_find_b_boxs(mask)
    if len(b_box) == 0:
        flag = False
    b_box = sorted(b_box, key=lambda box: box[4], reverse=True)  # 获取面积最大
    if flag:
        boxG = b_box[0]
        xG = boxG[0]
        l.append(xG)

    # 获取蓝色位置
    mask = cv2.inRange(img_hsv, thresholdItem[2][0], thresholdItem[2][1])
    mask = cv2.medianBlur(mask, 3)
    b_box = mask_find_b_boxs(mask)
    if len(b_box) == 0:
        flag = False
    b_box = sorted(b_box, key=lambda box: box[4], reverse=True)  # 获取面积最大
    if flag:
        boxB = b_box[0]
        xB = boxB[0]
        l.append(xB)

    if not flag:
        return [3, 2, 1]  # 默认

    r = []
    for i in range(3):
        min_value = min(l)  # 求列表最小值
        min_idx = l.index(min_value)
        r.append(min_idx + 1)
        l.remove(min_value)
    return r


def fineTuneItemF(threshold: list, ringRate: float, rank: list):
    # 设置相机参数
    cap = VideoCapture("/dev/cameraInc")
    reflashScreen("进行微调")
    while True:
        # 计算距离比例 # # # # # # # # # # # # # # #
        #  物料像素长宽要大于100
        frame = cap.read()

        # 匹配颜色
        img = cv2.GaussianBlur(frame, (3, 3), 0)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.erode(img_hsv, None, iterations=2)

        mask = cv2.inRange(img_hsv, threshold[rank[1]][0], threshold[rank[1]][1])
        mask = cv2.medianBlur(mask, 3)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=3)

        # 查找物块
        # # 找轮廓、去掉面积很小的，去掉长宽比例不合适的，选择y最大的, 
        # 太离谱的值要去掉重看，比如y特别小，
        b_box = mask_find_b_boxs(mask)
        box = get_the_most_credible_box(b_box)
        if box is None or len(box) == 0: continue
        lu, lv, w, h, s = box
        plu = tuple([lu, lv])
        pru = tuple([lu + w, lv])
        pld = tuple([lu, lv + h])
        prd = tuple([lu + w, lv + h])
        pc = tuple([lu + int(w / 2), lv + int(h / 2)])
        udx, udy = pc[0] - XCenter, pc[1] - YCenter
        # # 比例啥的不对得重拍，重拍要重新判断有没有在转
        # 面积太小, 离中心太远, 长宽比不对
        # img_note = img.copy()
        if w < 90 or h < 90 or s < 4000 or \
                lu == 0 and pc[1] > 240 or lv == 0 or lu + w == 640 and pc[1] > 240 or \
                max(w, h) / min(w, h) > 1.5:
            # cv2.rectangle(img_note, plu, prd, (0, 255, 255), 2)
            # print("当前找到的色块不符合条件, box: ", box, end='\r')
            # cv2.imwrite(f"/home/pi/GongXun/src/data/t21fineTuneItem/不符合要求的{k}.jpg" ,img_note)
            k += 1
            continue
        # 进行微调
        dx = int(udy * ringRate)  # dx > 0 往东走
        dy = int(-udx * ringRate)  # dy > 0 往南走
        if abs(udx) < 15 and abs(udy) < 15:  # 小于这个范围就不用微调了
            cmd = xmlReadCommand("calibrOk", 1)
            dx, dy = 0, 0
            print("当前要发送的命令是：", cmd, "udx, udy:", udx, udy, "dx, dy: (x10mm)", dx, dy)
            send_data(cmd, dx, dy)
            break  # 退出大循环
        else:  # 要微调
            cmd = xmlReadCommand("tweak", 1)
            print("当前要发送的命令是：", cmd, "udx, udy:", udx, udy, "dx, dy: (x10mm)", dx, dy)
            send_data(cmd, dx, dy)
            cv2.rectangle(img_note, plu, prd, (0, 255, 255), 2)
            cv2.imwrite(f"/home/pi/GongXun/src/data/t21fineTuneItem/微调{k}.jpg", img_note)
            wt_count += 1
            if wt_count > 5:
                cmd = xmlReadCommand("calibrOk", 1)
                print("微调次数大于5次, 强制退出")
                send_data(cmd, 0, 0)
                break
            start = time.time()
            while True:  # 等待调完信号
                end = time.time()
                if end - start > 5:
                    print("超时, 重新发送")
                    wt_count -= 1
                    break
                response = recv_data()
                print("等待调完信号, 当前接收: (", response, ")", end="\r")
                # print(" ", end='\r')
                if response == xmlReadCommand("tweakOk", 0):
                    print("\n当次微调动作完成                        ", end="\r")
                    break
                elif response == "Erro":
                    break
                if response == "OKOK":
                    print("************收到了OKOK************")
                else:
                    pass
                    # print("************没收到OKOK************")
    cap.terminate()
    time.sleep(0.2)


# def setItemF(threshold: list, queue: list, loop: int):
#     reflashScreen("放置物块中")
#     print("放置顺序:", queue)
#     XCenter, YCenter = xmlReadCenter()
#     ROI = [XCenter - 150, YCenter - 130, 300, 260]  # 待确定
#     color = ["红色", "绿色", "蓝色"]
#     colorCMD = ["sttR", "sttG", "sttB"]
#
#     # 设置相机参数
#     cap = VideoCapture("/dev/cameraInc")
#     # cap = cv2.VideoCapture("/dev/cameraInc")
#     # cap.set(3, 640)
#     # cap.set(4, 480)
#     # cap.set(cv2.CAP_PROP_AUTO_WB, 1)
#     # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
#     # capSet = cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
#     # if capSet:
#     #     print("相机参数设置成功")
#
#     n = 0  # 记录抓了几次
#     k = 0
#     cpl = [False, False, False]  # r, g, b
#     com_lish = {1: False, 2: False, 3: False}
#     accom_lish = []
#     while n < 3:
#         # 判断圆盘是否在转动 # # # # # # # # # # # #
#         last_frame = cap.read()
#         start_time = time.time()
#         is_plate_move = True
#         c = 0
#         while True:
#             end_time = time.time()
#             if end_time - start_time > 0.3:
#                 start_time = time.time()
#                 last_frame = cap.read()
#
#             current_frame = cap.read()
#             # 圆盘没在移动时退出
#             is_plate_move = moving_detect(last_frame, current_frame)
#             if is_plate_move:
#                 print("圆盘在动                           ", end='\r')
#                 c = 0
#             else:
#                 c += 1
#             if c > 15:
#                 break
#         # # # # # # # # # # # # # # # # # # # # # #
#
#         # 匹配颜色
#         frame = cap.read()
#         img = cv2.GaussianBlur(frame, (3, 3), 0)
#         img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         img_hsv = cv2.erode(img_hsv, None, iterations=2)
#
#         target_color = queue[n]
#         mask = cv2.inRange(img_hsv, threshold[target_color - 1][0], threshold[target_color - 1][1])
#         mask = cv2.medianBlur(mask, 3)
#         # kernel = np.ones((3, 3), np.uint8)
#         # mask = cv2.dilate(mask, kernel, iterations=3)
#
#         b_box = mask_find_b_boxs(mask)
#         box = get_the_most_credible_box(b_box)
#         if box is None:
#             continue
#         lu, lv, w, h, s = box
#         plu = tuple([lu, lv])
#         # pru = tuple([lu + w, lv])
#         # pld = tuple([lu, lv + h])
#         prd = tuple([lu + w, lv + h])
#         pc = tuple([lu + int(w / 2), lv + int(h / 2)])
#         udx, udy = pc[0] - XCenter, pc[1] - YCenter
#
#         img_note = img.copy()
#         if abs(udx) > 290 or abs(udy) > 210:
#             print("不符合条件", end='\r')
#             cv2.rectangle(img_note, plu, prd, (0, 255, 255), 2)
#             cv2.imwrite(f"/home/pi/GongXun/src/data/t22catchItem/不符合要求的{k}.jpg", img_note)
#             k += 1
#             continue
#         else:  # 可以抓取
#             cmd = xmlReadCommand(colorCMD[target_color - 1], 1)
#             send_data(cmd, 0, 0)
#             print("识别到", color[target_color - 1], "颜色正确, 进行放置")
#             reflashScreen(f"正在放置{color[target_color - 1]}")
#             print("将发送的命令为：", cmd)
#             # accom_lish.add(target_color)
#             n += 1
#             while True:
#                 response = recv_data()
#                 print("等待动作完成, 当前接收命令: [", response, "]", end='\r')
#                 # print("等待抓取动作完成, 当前接收命令:", response)
#                 if response is not None:
#                     if response == xmlReadCommand("mngOK", 0):
#                         print("抓取动作执行完毕, 进行下一步")
#                         break
#
#     cmd = xmlReadCommand("task2OK", 1)  # t2ok
#     print("三个物块都抓取完毕，发送:", cmd, "进行下一步")
#     reflashScreen(f"物块抓取完毕")
#     send_data(cmd, 0, 0)
#     cap.terminate()
#
#
# def catchItemF(threshold: list, queue: list, loop: int):
#     reflashScreen("抓取物块中")
#     print("抓取顺序:", queue)
#     XCenter, YCenter = xmlReadCenter()
#     ROI = [XCenter - 150, YCenter - 130, 300, 260]  # 待确定
#     color = ["红色", "绿色", "蓝色"]
#     colorCMD = ["catchR", "catchG", "catchB"]
#
#     # 设置相机参数
#     cap = VideoCapture("/dev/cameraInc")
#     # cap = cv2.VideoCapture("/dev/cameraInc")
#     # cap.set(3, 640)
#     # cap.set(4, 480)
#     # cap.set(cv2.CAP_PROP_AUTO_WB, 1)
#     # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
#     # capSet = cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
#     # if capSet:
#     #     print("相机参数设置成功")
#
#     n = 0  # 记录抓了几次
#     k = 0
#     cpl = [False, False, False]  # r, g, b
#     com_lish = {1: False, 2: False, 3: False}
#     accom_lish = []
#     while n < 3:
#         # 判断圆盘是否在转动 # # # # # # # # # # # #
#         last_frame = cap.read()
#         start_time = time.time()
#         is_plate_move = True
#         c = 0
#         while True:
#             end_time = time.time()
#             if end_time - start_time > 0.3:
#                 start_time = time.time()
#                 last_frame = cap.read()
#
#             current_frame = cap.read()
#             # 圆盘没在移动时退出
#             is_plate_move = moving_detect(last_frame, current_frame)
#             if is_plate_move:
#                 print("圆盘在动                           ", end='\r')
#                 c = 0
#             else:
#                 c += 1
#             if c > 15:
#                 break
#         # # # # # # # # # # # # # # # # # # # # # #
#
#         # 匹配颜色
#         frame = cap.read()
#         img = cv2.GaussianBlur(frame, (3, 3), 0)
#         img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         img_hsv = cv2.erode(img_hsv, None, iterations=2)
#
#         target_color = queue[n]
#         mask = cv2.inRange(img_hsv, threshold[target_color - 1][0], threshold[target_color - 1][1])
#         mask = cv2.medianBlur(mask, 3)
#         # kernel = np.ones((3, 3), np.uint8)
#         # mask = cv2.dilate(mask, kernel, iterations=3)
#
#         b_box = mask_find_b_boxs(mask)
#         box = get_the_most_credible_box(b_box)
#         if box is None:
#             continue
#         lu, lv, w, h, s = box
#         plu = tuple([lu, lv])
#         # pru = tuple([lu + w, lv])
#         # pld = tuple([lu, lv + h])
#         prd = tuple([lu + w, lv + h])
#         pc = tuple([lu + int(w / 2), lv + int(h / 2)])
#         udx, udy = pc[0] - XCenter, pc[1] - YCenter
#
#         img_note = img.copy()
#         if abs(udx) > 290 or abs(udy) > 210:
#             print("不符合条件", end='\r')
#             cv2.rectangle(img_note, plu, prd, (0, 255, 255), 2)
#             cv2.imwrite(f"/home/pi/GongXun/src/data/t22catchItem/不符合要求的{k}.jpg", img_note)
#             k += 1
#             continue
#         else:  # 可以抓取
#             cmd = xmlReadCommand(colorCMD[target_color - 1], 1)
#             send_data(cmd, 0, 0)
#             print("识别到", color[target_color - 1], "颜色正确, 进行抓取")
#             reflashScreen(f"正在抓取{color[target_color - 1]}")
#             print("将发送的命令为：", cmd)
#             # accom_lish.add(target_color)
#             n += 1
#             while True:
#                 response = recv_data()
#                 print("等待抓取动作完成, 当前接收命令: [", response, "]", end='\r')
#                 # print("等待抓取动作完成, 当前接收命令:", response)
#                 if response is not None:
#                     if response == xmlReadCommand("mngOK", 0):
#                         print("抓取动作执行完毕, 进行下一步")
#                         break
#
#     cmd = xmlReadCommand("task2OK", 1)  # t2ok
#     print("三个物块都抓取完毕，发送:", cmd, "进行下一步")
#     reflashScreen(f"物块抓取完毕")
#     send_data(cmd, 0, 0)
#     cap.terminate()


if __name__ == "__main__":
    # print(cv2.__version__)
    # capture(0, "测试照片2")
    pass
