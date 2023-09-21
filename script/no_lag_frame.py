import cv2
import numpy as np
import queue
import threading
import time


# 自定义无缓存读视频类
class VideoCapture:
    """Customized VideoCapture, always read latest frame """
    
    def __init__(self, camera_id):
        # "camera_id" is a int type id or string name
        self.cap = cv2.VideoCapture(camera_id)
        self.q = queue.Queue(maxsize=3)
        self.stop_threads = False    # to gracefully close sub-thread
        th = threading.Thread(target=self._reader)
        th.daemon = True             # 设置工作线程为后台运行
        th.start()

    # 实时读帧，只保存最后一帧
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
    

def get_circle_center(img):
    result = []
    img_calc = cv2.GaussianBlur(img, (5, 5), 0)
    img_gray = cv2.cvtColor(img_calc, cv2.COLOR_BGR2GRAY)
    img_binary = cv2.adaptiveThreshold(~img_gray, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
    erode_kernel = np.ones((1, 1), dtype=np.uint8)
    erosion_binary = cv2.erode(img_binary, kernel=erode_kernel, iterations=1)
    cv2.imshow("video in deal", erosion_binary)
    circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)
    if circles is not None and len(circles) != 0:
        circles = np.round(circles[0, :]).astype('int')
        for (x, y, r) in circles:
            result.append(tuple([x, y]))
    return result


if __name__ == "__main__":        
    # 测试自定义VideoCapture类
    cameraTop = '/dev/cameraTop'
    cap = VideoCapture(cameraTop)

    while True:
        frame = cap.read()
        circles = get_circle_center(frame)
        for x, y in circles:
            cv2.circle(frame, (x, y), 3, (0,0,255), 1)
        # time.sleep(0.05)   # 模拟耗时操作，单位：秒   
        cv2.imshow("frame", frame)
        if chr(cv2.waitKey(1)&255) == 'q':  # 按 q 退出
            cap.terminate()
            break
