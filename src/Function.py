import cv2
import numpy as np
import queue, threading, struct
from pyzbar.pyzbar import decode
from pyzbar import pyzbar


class VideoCapture:
    def __init__(self, camera_id):
        # "camera_id" is a int type id or string name
        self.cap = cv2.VideoCapture(camera_id)
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


def getCircleCenter(img:np.ndarray) -> [(np.float32, np.float32), ...]:
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


def unDistort(img):
    DIM = (640, 480)
    K = np.array(
        [[529.0542108650583, 0.0, 328.11243708259155], [0.0, 528.4474102469408, 276.541015762088], [0.0, 0.0, 1.0]])
    D = np.array([[-0.1675384798926949], [-0.5110533326571545], [10.49841774261518], [-41.314556160738114]])
    h, w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # cv2.imshow("undistorted", undistorted_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return undistorted_img


def getQRCodeResult(img):
    if img is None:
        print("QRCode Module Error: img is empty!")
        return None
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result = decode(img_gray)
    # result_list = []
    if result is not None and len(result) != 0:
        for item in result:
            return item.data.decode("utf-8")
            # result_list.append(item.data.decode("utf-8"))
    else:
        print("No QR Code Found.")


def parseItemCatchQueue(qr_result, q1, q2):
    # 假设载物盘为正三角形
    # 抓取顺序和放置顺序一样
    color = {'1': 'r', '2': 'g', '3': 'b'}
    queue_list = qr_result.split("+")
    q1s, q2s = queue_list
    for c in q1s:
        q1.append(color[c])
    for c in q2s:
        q2.append(color[c])
    # 抓取顺序和放置顺序不一样


#定义数据包，格式为2个帧头+4个字符数据+2个半整型数据+帧尾（11byte）
#4个字符传输命令名，2个int传输xy方向的偏差
def send_data(uart, cmd, i, f):
    a, b, c, d = cmd
    data = struct.pack("<bbbbbbhhb", # 四个字符作为命令, 两个浮点作为xy偏差
                        0x2C,      # 帧头1      ','
                        0x3C,      # 帧头2      '<'
                        ord(str(a)), # 字符1
                        ord(str(b)), # 字符2
                        ord(str(c)), # 字符3
                        ord(str(d)), # 字符4
                        int(i), # 半整型数据1
                        int(f), # 半整型数据2
                        0x3E)      # 帧尾       '>'
    uart.write(data)


# 图像预处理
def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


# 获取命令
def getMessage(node, tag):
    _res = node.find(tag).text
    _res = [_ for _ in _res]
    return _res


# bbox: [box1, box2, ...]
# box: [左上角点x, 左上角点y, 宽度, 高度, ...]
def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(_mask, connectivity=8)  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


# 获取阈值
def getColorThreshold(root, tag, rank):
    _min, _max = [], []
    colorNode = root.find(f'color[@category="{tag}"]')
    floors = colorNode.findall('./*/floor')
    ceilings = colorNode.findall('./*/ceiling')
    for i in range(3):
        _min.append(int(floors[i].text))
        _max.append(int(ceilings[i].text))
    _min = np.array(_min)
    _max = np.array(_max)
    rank[0] = _min
    rank[1] = _max


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


def uDistanceToDx(ud, h):
    if h == 16:
        return int(ud * 25 / 120 * 10)
    elif h == 30:
        return 0
    else:
        return 0


if __name__ == "__main__":
    pass
