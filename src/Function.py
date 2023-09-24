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
            result.append(tuple([x, y]))
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


def send_data(uart, a, b, c, d, e, f):
    data = struct.pack("<bbbbbbhhb", # 四个字符作为命令, 两个浮点作为xy偏差
                    0x2C, # 帧头
                       0x3C,     # 帧头
                       ord(a), # 字符1
                       ord(b), # 字符2
                       ord(c), # 字符3
                       ord(d), # 字符4
                       np.short(e), # 浮点数据1
                       np.short(f), # 浮点数据2
                       0x4C) # 帧尾
    
    print(data)
#定义数据包，格式为2个帧头+4个字符数据+2个半整型数据+帧尾（11byte）
#4个字符传输命令名，2个int传输xy方向的偏差
def send_data(uart, a, b, c, d, i, f):
    data = struct.pack("<bbbbbbffb", # 四个字符作为命令, 两个浮点作为xy偏差
                        0x2C,      # 帧头1
                        0x3C,      # 帧头2
                        ord(str(a)), # 字符1
                        ord(str(b)), # 字符2
                        ord(str(c)), # 字符3
                        ord(str(d)), # 字符4
                        int(i), # 半整型数据1
                        int(f), # 半整型数据2
                        0x4C)      # 帧尾
    uart.write(data)


if __name__ == "__main__":
    pass
