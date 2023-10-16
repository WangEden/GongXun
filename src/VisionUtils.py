import numpy as np
import cv2


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

    if mode == 1:  # 拍的时候就进行预处理
        frame = precondition(frame)

    cv2.imwrite(f"/home/pi/GongXun/src/data/{name}.jpg", frame)
    print("拍照完成, 图片保存成功")
    cap.release()
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
    YCenter = 220
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
    img_gray = cv2.cvtColor(img_calc, cv2.COLOR_BGR2GRAY)
    img_binary = cv2.adaptiveThreshold(~img_gray, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
    erode_kernel = np.ones((1, 1), dtype=np.uint8)
    erosion_binary = cv2.erode(img_binary, kernel=erode_kernel, iterations=1)
    # cv2.imshow("video in deal", erosion_binary)
    circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)
    if len(circles) != 0:
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

    
def color2colorDistance(tag1: str, tag2: str):
    # r: 1, g: 2, b: 3
    color = {'r': 1, 'g': 2, 'b': 3}
    return abs(color[tag1] - color[tag2]) * 1500  # x10mm      


if __name__ == '__main__':
    pass