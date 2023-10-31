import numpy as np
import cv2
import queue, threading
from XmlProcess import xmlReadCenter
from PIL import Image, ImageDraw, ImageFont

lastContent = ""
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

    # print(cap.set(3, 640))
    cap.set(3, 640)
    cap.set(4, 480)
    cap.set(cv2.CAP_PROP_AUTO_WB, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))

    ret, frame = cap.read()
    if not ret:
        print("**摄像头打开失败**")
        return False

    if mode == 1:  # 拍的时候就进行预处理
        frame = precondition(frame)

    cv2.imwrite(f"/home/pi/GongXun/src/data/{name}.jpg", frame)
    print("拍照完成, 图片保存成功")
    cap.release()
    return True


# 判断前后两个画面是否有物体在运动
def moving_detect(frame1, frame2) -> bool:
    img1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    grey_diff = cv2.absdiff(img1, img2)  # 计算两幅图的像素差
    change = np.average(grey_diff)

    if change > 3:  # 当两幅图的差异大于给定的值后，认为画面有物体在动
        return True
    else:
        return False


# 图像预处理
def precondition(_img):
    # _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    # _ = cv2.GaussianBlur(_, (3, 3), 0)
    _ = cv2.GaussianBlur(_img, (3, 3), 0)
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


def mask_find_b_boxs2(_mask):
    contours, hierarchy = cv2.findContours(_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    box_list = []
    b_box = []
    for c in contours:
        if cv2.contourArea(c) < 4500:  # 过滤掉较面积小的物体
            continue
        else:
            box_list.append(c)
    for i in box_list:
        rect = cv2.minAreaRect(i)
        box = cv2.boxPoints(rect)
        b_box.append(box)
        # cv2.drawContours(img_note, [np.int0(box)], -1, (0, 255, 255), 2)
    return b_box


# 按照面积、位置筛选得到最可信的外接矩形
def get_the_most_credible_box(b_box):
    XCenter, YCenter = xmlReadCenter()
    if len(b_box) == 0:
        return None
    if len(b_box) == 1:
        return b_box[0]
    boxs = []
    for i, v in enumerate(b_box):
        lu, lv, w, h, s = b_box[i]
        if b_box[i][4] > 1000 and max(w, h) / min(w, h) < 1.5 and lv + h < 640:
            boxs.append(b_box[i])
    if len(boxs) == 0:
        return None
    b_box = sorted(b_box, key=lambda box: box[4], reverse=True)
    # print("by area:\n", b_box)
    b_box = sorted(boxs, key=lambda box: abs(box[0] + box[2] / 2 - XCenter))
    # print("by dx:\n", b_box)
    b_box = sorted(b_box, key=lambda box: abs(box[1] + box[3] / 2 - YCenter))
    # print("by dy:\n", b_box)
    b_box = sorted(b_box, key=lambda box: box[1], reverse=True)
    # print("by y:\n", b_box)
    flag = False
    if len(b_box) >= 3:
        b_box = b_box[:2]  # 取前三个面积大的
    elif len(b_box) == 2:
        print("只有两个")

        flag = True
    # if flag:
    #     a = 
    return b_box[0]


# 按照面积、位置筛选得到最可信的外接矩形
def get_the_most_credible_box2(b_box):  # 用于粗加工区
    XCenter, YCenter = xmlReadCenter()
    if len(b_box) == 0:
        return None
    if len(b_box) == 1:
        return b_box[0]
    boxs = []
    for i, v in enumerate(b_box):
        lu, lv, w, h, s = b_box[i]
        if b_box[i][4] > 1000 and max(w, h) / min(w, h) < 1.5:
            boxs.append(b_box[i])
    if len(boxs) == 0:
        return None
    b_box = sorted(b_box, key=lambda box: box[4], reverse=True)
    # print("by area:\n", b_box)
    b_box = sorted(boxs, key=lambda box: abs(box[0] + box[2] / 2 - XCenter))
    # print("by dx:\n", b_box)
    b_box = sorted(b_box, key=lambda box: abs(box[1] + box[3] / 2 - YCenter))
    # print("by dy:\n", b_box)
    b_box = sorted(b_box, key=lambda box: box[1], reverse=True)
    # print("by y:\n", b_box)
    flag = False
    if len(b_box) >= 3:
        b_box = b_box[:2]  # 取前三个面积大的
    elif len(b_box) == 2:
        print("只有两个")
        flag = True
    # if flag:
    #     a = 
    return b_box[0]


# 判断一个矩形是否被另一个矩形包围
def compRect(roi, box):
    # print("roi: ", roi, "box: ", box)
    if box is None:
        return False
    if len(box) == 0:
        return False
    if roi[0] < box[0] and \
        roi[1] < box[1] and \
        (roi[0] + roi[2]) > (box[0] + box[2]) and \
        (roi[1] + roi[3]) > (box[1] + box[3]):
        return True
    else:
        return False


# 判断一个二值图像形状的和一个区域的重合率
def f(mask, box, tag):
    __ = np.zeros(mask.shape, dtype=np.uint8)
    lx, ly, w, h, s1 = box
    cx, cy = int(lx + w / 2), int(ly + h / 2)
    r = max(w, h)
    if tag == 'Circle':
        __ = cv2.circle(__, (cx, cy), r, (255, 255, 255), -1)
        __ = cv2.bitwise_and(__, __)
        return s1 / mask_find_b_boxs(__)[0][4]
    elif tag == 'Hexagon':  # 其他形状还没写
        pass


# 获取色环的圆心像素坐标
def getCircleCenter(img:np.ndarray):
    result = []
    img_calc = cv2.GaussianBlur(img, (5, 5), 0)
    img_calc = img
    img_gray = cv2.cvtColor(img_calc, cv2.COLOR_BGR2GRAY)
    
    img_binary = cv2.adaptiveThreshold(~img_gray, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
    erode_kernel = np.ones((1, 1), dtype=np.uint8)
    erosion_binary = cv2.erode(img_binary, kernel=erode_kernel, iterations=1)
    # cv2.imshow("video in deal", erosion_binary)
    circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)
    
    # circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1, 100)
    if circles is not None and len(circles) != 0:
        circles = np.round(circles[0, :]).astype('int')
        for (x, y, r) in circles:
            result.append(tuple([x, y, r]))
    return result


# 利用K-means算法找出k个最准确的圆心
def getKmeansCenter(k:int, lis:[(np.float32, np.float32), ...]) -> [(int, int), ...]:
    lis = np.float32(np.array(lis))
    # 定义终止条件
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # 定义初始中心选择方式
    flag = cv2.KMEANS_PP_CENTERS
    compactness, labels, centers = cv2.kmeans(lis, k, None, criteria, 10, flag)
    result = np.round(centers, 0).astype(int).tolist()
    # print(centers)
    return result

    
def get_the_most_credible_circle(clcList: list):
    XCenter, YCenter = 320, 220
    if len(clcList) == 0:
        return None
    if len(clcList) == 1:
        return clcList[0]
    
    clcList = sorted(clcList, key=lambda clc: abs(clc[0] - XCenter))
    # print("by dx:\n", clcList)
    clcList = sorted(clcList, key=lambda clc: abs(clc[1] - YCenter))
    # print("by dy:\n", clcList)
    return clcList[0]


class VideoCapture:
    def __init__(self, camera_id):
        # "camera_id" is a int type id or string name
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
        # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cap.set(6, cv2.VideoWriter.fourcc(*"MJPG"))
        self.q = queue.Queue(maxsize=3)
        self.stop_threads = False    # to gracefully close sub-thread
        th = threading.Thread(target=self._reader)
        th.daemon = True             # 设置工作线程为后台运行
        th.start()

    def _reader(self):
        while not self.stop_threads:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait() 
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()
    
    def terminate(self):
        self.stop_threads = True
        self.cap.release()


def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if text == "":
        return img
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "./data/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle, stroke_width=2)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def reflashScreen(string):
    global lastContent
    screen = cv2.imread("./data/screen_template.jpg")
    if screen is None:
        screen = np.ones((600, 1024), dtype=np.uint8) * 255
    dx1 = len(lastContent) * 20
    dx2 = len(string) * 30
    Px1 = 512 - dx1
    Px2 = 512 - dx2
    Py1 = 230
    Py2 = 270
    screen = cv2AddChineseText(screen, lastContent, (Px1, Py1), (64, 64, 64), 30)
    screen = cv2AddChineseText(screen, string, (Px2, Py2), (0, 0, 0), 60)
    lastContent = string
    cv2.imwrite("./data/screen.jpg", screen)


if __name__ == '__main__':
    pass
