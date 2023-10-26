import time
import numpy as np
import cv2
from XmlProcess import *
from VisionUtils import *


# # 设置相机参数
# cap = cv2.VideoCapture(0)
# # cap.set(3, 640)
# # cap.set(4, 480)
# # cap.set(cv2.CAP_PROP_AUTO_WB, 1)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
# # capSet = cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
# # if capSet:
# #     print("相机参数设置成功")

# rate = 1
# # 再套一层while
# k = 0
# wt_count = 0
# XCenter, YCenter = 320, 240
# reflashScreen("进行微调")
# # while True:
# # 判断圆盘是否在转动 # # # # # # # # # # # #
# ret, last_frame = cap.read()
# # last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
# start_time = time.time()
# is_plate_move = True
# c = 0
# while True:
#     end_time = time.time()
#     if end_time - start_time > 0.2:
#         start_time = time.time()
#         ret, last_frame = cap.read()

#     ret, current_frame = cap.read()
#     cv2.imshow("c", current_frame)
#     cv2.waitKey(24)
#     # 圆盘没在移动时退出
#     is_plate_move = moving_detect(last_frame, current_frame)
#     if not is_plate_move:
#         c += 1
#     if c > 10:
#         break
# cap.release()
# cv2.destroyAllWindows()
# # # # # # # # # # # # # # # # # # # # # #
# img_path = "take4.jpg"
# img = cv2.imread(img_path)
#
#
# def mouseHandler(e, x, y, f, p):
#     if e == cv2.EVENT_LBUTTONDOWN:
#         print("click: ", x, y)
#
#
# cv2.namedWindow("img")
# cv2.setMouseCallback("img", mouseHandler)
#
#
# cv2.imshow("img", img)
# cv2.waitKey(0)
#
#
# # 获取三个物块的阈值
# threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
# for i, c in enumerate(["red", "green", "blue"]):
#     xmlReadThreshold("item", c, threshold[i])
#
#
# # img = cv2.pyrMeanShiftFiltering(img, 15, 20)
# img = cv2.GaussianBlur(img, (3, 3), 0)
# img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# img_hsv = cv2.erode(img_hsv, None, iterations=2)
#
# # threshold[0] = [np.array([152, 114, 95], np.array([233, 228, 220]))]
#
# mask1 = cv2.inRange(img_hsv, threshold[0][0], threshold[0][1])
# # mask1 = cv2.medianBlur(mask1, 3)
# # cv2.imshow("mask1", mask1)
# mask2 = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
# mask2 = cv2.medianBlur(mask2, 3)
# # cv2.imshow("mask2", mask2)
# mask3 = cv2.inRange(img_hsv, threshold[2][0], threshold[2][1])
# mask3 = cv2.medianBlur(mask3, 3)
# # cv2.imshow("mask3", mask3)
# mask = mask1 + mask2 + mask3
# kernel = np.ones((3, 3), np.uint8)
# mask = cv2.dilate(mask, kernel, iterations=3)
#
# cv2.imshow("mask", mask)
# cv2.waitKey(0)
#
# img_note = img.copy()
#
# # b_box = mask_find_b_boxs2(mask)
# # for box in b_box:
# #     box = np.int0(box)
# #     cv2.drawContours(img_note, [np.int0(box)], -1, (0, 255, 255), 2)
#
# b_box = mask_find_b_boxs(mask)
# box = get_the_most_credible_box(b_box)
# b_box = mask_find_b_boxs(mask)
# box = get_the_most_credible_box(b_box)
#
# lu, lv, w, h, s = box
# p1 = tuple([lu, lv])
# p2 = tuple([lu + w, lv + h])
#
# print("box:", box)
# cv2.rectangle(img_note, p1, p2, (0, 255, 255), 2)
#
# XCenter, YCenter = 320, 240
# ROI = [XCenter - 160, YCenter - 160, 320, 320]  # 待确定
# lu, lv, w, h= ROI
# p1 = tuple([lu, lv])
# p2 = tuple([lu + w, lv + h])
# cv2.rectangle(img_note, p1, p2, (255, 0, 0), 2)
# cv2.imshow("note", img_note)
# cv2.waitKey(0)


# cap = VideoCapture("/dev/cameraInc")  # 读取视频文件，参数设置为0表示从摄像头获取图像


# def moving_detect(frame1, frame2):
#     img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
#     img2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
#     grey_diff = cv2.absdiff(img1, img2)  # 计算两幅图的像素差
#     change = np.average(grey_diff)

#     if change > 3:  # 当两幅图的差异大于给定的值后，认为画面有物体在动
#         cv2.putText(frame2, 'moving', (100, 30), 2, 1, (0, 255, 0), 2, cv2.LINE_AA)
#     else:
#         cv2.putText(frame2, 'quiet', (100, 30), 2, 1, (255, 0, 0), 2, cv2.LINE_AA)
#     cv2.imshow("output", frame2)


# frame1 = cap.read()
# img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # 将图片转为灰度图，第一个返回值表示是否转换成功，第二个返回值就是灰度图了
# start = time.time()
# while True:
#     end = time.time()
#     if (end - start > 0.3):  # 每隔2秒拍一幅图，比较前后两幅图的差异
#         start = time.time()
#         frame1 = cap.read()

#     frame2 = cap.read()
#     moving_detect(frame1, frame2)
#     if cv2.waitKey(5) & 0xFF == ord('q'):  # 按下q停止运行程序
#         break


# # 最后，关闭所有窗口
# cap.release()
# cv2.destroyAllWindows()

#################################################################


# import cv2
# import numpy as np


# cap = VideoCapture("/dev/cameraInc")
# # cap.set(3, 640)
# # cap.set(4, 480)
# # cap.set(cv2.CAP_PROP_AUTO_WB, 1)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
# # cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))


# # 获取三个色环阈值
# threshold = [[], [], []]  # -> [[min, max], [min, max], [min, max]]
# for i, c in enumerate(["red", "green", "blue"]):
#     xmlReadThreshold("ring", c, threshold[i])

# try:
#     while True:
#         img = cap.read()
#         # if ret:
#         # img = precondition(img) # 耗时
#         # img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         # img_hsv = cv2.erode(img_hsv, None, iterations=2)
#         # maskGreen = cv2.inRange(img_hsv, threshold[1][0], threshold[1][1])
#         cv2.line(img, (0, 280), (640, 280), (255, 0, 0), 2)
#         cv2.line(img, (275, 0), (275, 480), (255, 0, 0), 2)
#         cv2.imshow("look", img)
#         cv2.waitKey(24)

# except:
#     cap.terminate()
# finally:
#     cap.terminate()

#################################################################

# # debug # # # # # # # # # # # # # # # # # #
# debug = 0
with open("/home/pi/color.txt", "r") as file:
    s = file.read()
    print("color: ", s)
# # # # # # # # # # # # # # # # # # # # # # #



#################################################################
