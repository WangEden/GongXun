import math
import cv2
import numpy as np
from math import acos
from Functions import Functions


class Dashboard:
    def __init__(self, img_path):
        self._img_path = img_path
        self._image = cv2.imread(self._img_path)
        self.circleData = []
        self.centerX, self.centerY, self.chanel = self._image.shape
        self.scaleImg, self.pointImg = None, None
        self.scaleCnt, self.pointCnt = [], []
        self.pointAngle, self.minScaleAngle, self.maxScaleAngle = 360, 360, 0
        self.DataType, self.Unit, self.Span = 'Stress', 'Pa', 25
        self.OutData = None
        self.OutImage = None

    def cut_off_the_circle_panel(self):
        # 涂抹
        # dst = cv2.pyrMeanShiftFiltering(image, 15, 20)
        # cimage = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        # 转灰度图
        cimage = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('image', cimage)
        # cv2.waitKey()

        # 查找圆边轮廓
        circles = cv2.HoughCircles(cimage, cv2.HOUGH_GRADIENT, 1, 80, param1=100, param2=20, minRadius=10, maxRadius=0)
        r_1 = circles[0, 0, 2]
        c_x = circles[0, 0, 0]
        c_y = circles[0, 0, 1]
        self.circleData = [c_x, c_y, r_1]
        # 创建白幕遮罩
        circle = np.ones(self._image.shape, dtype="uint8")
        circle = circle * 255
        # print(type(circle))
        # 画出查找到的实心霍夫圆
        cv2.circle(circle, (int(c_x), int(c_y)), int(r_1), (0, 0, 0), -1)
        # 将遮罩与原图像做差裁剪图像
        bitwiseOr = cv2.bitwise_or(self._image, circle)

        # cv2.imshow('image', bitwiseOr)
        # cv2.waitKey()
        self._image = bitwiseOr
        # return bitwiseOr

    def extrac_contours(self):
        _img = cv2.GaussianBlur(self._image, (3, 3), 0)
        grayImg = cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY)

        # 自适应阈值提取轮廓
        binary = cv2.adaptiveThreshold(~grayImg, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)

        # 对轮廓进行腐蚀
        erode_kernel = np.ones((3, 3), dtype=np.uint8)
        erosion_binary = cv2.erode(binary, kernel=erode_kernel, iterations=1)

        # 显示侵蚀后的图像
        self.OutImage = erosion_binary
        # cv2.imshow('image2', erosion_binary)
        # cv2.waitKey()

        # 查找轮廓
        contours, hierarchy = cv2.findContours(erosion_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # 轮廓查找
        # print(len(contours))
        # print(img.shape)

        # 筛选轮廓
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            ptrI, (w, h), c = rect
            if w == 0 or h == 0:
                continue

            if (ptrI[0] - self.circleData[0]) ** 2 + (ptrI[1] - self.circleData[1]) ** 2 > 0.81 * (self.circleData[2] ** 2):
                continue

            if (ptrI[0] - self.circleData[0]) ** 2 + (ptrI[1] - self.circleData[1]) ** 2 < 0.36 * (self.circleData[2] ** 2):
                continue

            if w * h < 40:
                continue

            if (ptrI[0] - self.circleData[0]) ** 2 + (ptrI[1] - self.circleData[1]) ** 2 < 0.49 * (self.circleData[2] ** 2):
                # print('s:'+str(w * h))
                if w / h > 8 or h / w > 8:  # 指针
                    # print('w or h: ' + str(w) + ' or ' + str(h))
                    # print('point_angle: '+str(270 - (c + 90)))
                    self.pointCnt.append(contour)
            elif w / h > 4 or h / w > 4:  # 刻度线
                self.scaleCnt.append(contour)
                # print('scale_angle: ' + str(270 - (c + 90)))

        # 生成掩膜
        mask1 = np.zeros(_img.shape[0:2], np.uint8)
        mask2 = np.zeros(_img.shape[0:2], np.uint8)
        sMask = cv2.drawContours(mask1, self.scaleCnt, -1, (255, 255, 255), -1)
        pMask = cv2.drawContours(mask2, self.pointCnt, -1, (255, 255, 255), -1)

        # cv2.imshow('image2', sMask)
        # cv2.waitKey()

        # cv2.imshow('image2', pMask)
        self.scaleImg, self.pointImg = sMask, pMask
        return erosion_binary


    def get_angle(self):
        if len(self.pointCnt) == 0 or len(self.scaleCnt) == 0:
            print('e:len=0')
            return

        cX, cY, cR = self.circleData
        ptrPoint = cv2.minAreaRect(self.pointCnt[0])[0]
        ptrCenter = (cX, cY)
        ptrRef = (cX, cY + cR)
        lenAB = Functions.Disttances(ptrPoint, ptrCenter)
        lenAC = Functions.Disttances(ptrPoint, ptrRef)
        lenBC = Functions.Disttances(ptrRef, ptrCenter)

        angleB = acos((lenAB ** 2 + lenBC ** 2 - lenAC ** 2) / (2 * lenAB * lenBC))
        if ptrPoint[0] > cX:
            angleB = math.pi * 2 - angleB

        self.minScaleAngle = 2 * math.pi
        self.maxScaleAngle = 0
        for scale_cnt in self.scaleCnt:
            ptrScale = cv2.minAreaRect(scale_cnt)[0]
            len1 = Functions.Disttances(ptrScale, ptrCenter)
            len2 = Functions.Disttances(ptrScale, ptrRef)
            len3 = Functions.Disttances(ptrRef, ptrCenter)
            angle = acos((len1 ** 2 + len3 ** 2 - len2 ** 2) / (2 * len1 * len3))
            if ptrScale[0] > cX:
                angle = math.pi * 2 - angle
            if self.minScaleAngle > angle:
                self.minScaleAngle = angle
            if self.maxScaleAngle < angle:
                self.maxScaleAngle = angle
            # print(angle / math.pi * 180)

        self.pointAngle = angleB / math.pi * 180
        self.minScaleAngle = self.minScaleAngle / math.pi * 180
        self.maxScaleAngle = self.maxScaleAngle / math.pi * 180
        # print('saMin: ' + str(self.minScaleAngle) + '°', 'saMax: ' + str(self.maxScaleAngle) + '°',
        #       'pa: ' + str(self.pointAngle) + '°')


    def calculate(self):
        rate = (self.pointAngle - self.minScaleAngle) / (self.maxScaleAngle - self.minScaleAngle)
        self.OutData = self.DataType + ': ' + str(rate * self.Span) + ' ' + self.Unit
        # print(self.OutData)


    def handle(self):
        self.cut_off_the_circle_panel()
        self.extrac_contours()
        self.get_angle()
        self.calculate()
        return self.OutImage, self.OutData


# if __name__ == '__main__':
#     dashboard = Dashboard('images/Dashboard/60.jpg')
#     img, data = dashboard.handle()
#     cv2.namedWindow("image")
#     print(data)
#     cv2.imshow('image', img)
#     cv2.waitKey()
