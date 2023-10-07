#!/usr/bin/env python
# -*- coding:utf-8 -*-
import cv2
import numpy as np
import glob

# 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 30, 0.001)

w=10
h=8

# 获取标定板角点的位置
objp = np.zeros(((w-1) * (h-1), 3), np.float32)  #格子数为10行8列，内角点为9*7的棋盘格图片
objp[:, :2] = np.mgrid[0:(h-1), 0:(w-1)].T.reshape(-1, 2)  # 将世界坐标系建在标定板上，所有点的Z坐标全部为0，所以只需要赋值x和y

obj_points = []  # 存储3D点
img_points = []  # 存储2D点

images = glob.glob("./biaoding/*.jpg")
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size = gray.shape[::-1]
    ret, corners = cv2.findChessboardCorners(gray, ((w-1) , (h-1)), None)  #提取角点:第一个参数为图片，第二个为图片横纵角点的个数。

    if ret:
        obj_points.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)  # 在原角点的基础上寻找亚像素角点
        # 找寻亚像素角点：cornerSubPix(gray, corners, (winsize, winsize), (-1, -1), criteria)
        # winsize为搜索窗口边长的一半。
        # zeroZone：搜索区域中间的dead region边长的一半，有时用于避免自相关矩阵的奇异性。如果值设为(-1,-1)则表示没有这个区域。
        # criteria：角点精准化迭代过程的终止条件。也就是当迭代次数超过criteria.maxCount，或者角点位置变化小于criteria.epsilon时，停止迭代过程。

        if [corners2]:
            img_points.append(corners2)
        else:
            img_points.append(corners)

        cv2.drawChessboardCorners(img, ((w-1) , (h-1)), corners, ret)  # 记住，OpenCV的绘制函数一般无返回值
        # 可以使用该函数把角点画出来：drawChessboardCorners(image, (w, h), corners, ret);其中corners和ret为第一个函数的输出值。
        cv2.imshow('img', img)
        cv2.waitKey(0) # 直到你按下任意一个键，才被关掉
        # 在delaytime时间内,按键盘,返回所按键的ASCII值; 若未在delaytime时间内按任何键,返回-1; 其中,dalaytime: 单位ms

print (len(img_points))
cv2.destroyAllWindows()

# 标定
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)

print ("ret:", ret)
print ("mtx:\n", mtx)  # 内参数矩阵
print ("dist:\n", dist)  # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
print ("rvecs:\n", rvecs)  # 旋转向量  # 外参数
print ("tvecs:\n", tvecs)  # 平移向量  # 外参数

print("-----------------------------------------------------")

# 畸变校正
img = cv2.imread(images[9])
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))  #显示更大范围的图片（正常重映射之后会删掉一部分图像）
print (newcameramtx)

print("------------------使用undistort函数-------------------")
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
x, y, w, h = roi
dst1 = dst[y:y + h, x:x + w]
cv2.imwrite('calibresult21.jpg', dst1)
print ("方法一:dst的大小为:", dst1.shape)

'''
# undistort方法二
print("-------------------使用重映射的方式-----------------------")
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)  # 获取映射方程
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)      # 重映射
# dst = cv2.remap(img, mapx, mapy, cv2.INTER_CUBIC)  # 重映射后，图像变小了
x, y, w, h = roi
dst2 = dst[y:y + h, x:x + w]
cv2.imwrite('calibresult22.jpg', dst2)
print "方法二:dst的大小为:", dst2.shape  # 图像比方法一的小
'''
print("-------------------计算反向投影误差-----------------------")
tot_error = 0
for i in xrange(len(obj_points)):
    img_points2, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(img_points[i], img_points2, cv2.NORM_L2) / len(img_points2)
    tot_error += error

mean_error = tot_error / len(obj_points)
print ("total error: ", tot_error)
print ("mean error: ", mean_error)
