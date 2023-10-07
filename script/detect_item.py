import cv2
import numpy as np
from xml.etree import ElementTree as ET
import queue, threading, struct


class VideoCapture:
    def __init__(self, camera_id):
        # "camera_id" is a int type id or string name
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))
        self.q = queue.Queue(maxsize=3)
        self.stop_threads = False  # to gracefully close sub-thread
        th = threading.Thread(target=self._reader)
        th.daemon = True  # 设置工作线程为后台运行
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


img_path = "15.jpg"
camera = "/dev/cameraInc"
# cap = cv2.VideoCapture(camera)
cap = VideoCapture(0)


thresholdNode = ET.parse(source='threshold.xml').find('threshold[@tag="item"]')
redThreshold = [None, None]
greenThreshold = [None, None]
blueThreshold = [None, None]
XCenter = 320
YCenter = 240


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


def precondition(_img):
    _ = cv2.pyrMeanShiftFiltering(_img, 15, 20)
    _ = cv2.GaussianBlur(_, (3, 3), 0)
    return _


# bbox: [box1, box2, ...]
# box: [左上角点x, 左上角点y, 宽度, 高度, ...]
def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(_mask, connectivity=8)  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


def get_the_most_credible_box(b_box):
    global XCenter, YCenter
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


if __name__ == '__main__':
    getColorThreshold(thresholdNode, 'red', redThreshold)
    getColorThreshold(thresholdNode, 'green', greenThreshold)
    getColorThreshold(thresholdNode, 'blue', blueThreshold)

    while True:
        frame = cap.read()
        if frame is None:
            continue
        img_bgr = precondition(frame)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(img_hsv, blueThreshold[0], blueThreshold[1])
        mask = cv2.medianBlur(mask, 3)
        bbox = mask_find_b_boxs(mask)
        img_note = frame.copy()

        most_credible_box = get_the_most_credible_box(bbox)
        if most_credible_box is not None:
            p1 = tuple([most_credible_box[0], most_credible_box[1]])
            p2 = tuple([most_credible_box[0] + most_credible_box[2], most_credible_box[1] + most_credible_box[3]])
            cx = int((p1[0] + p2[0]) / 2)
            cy = int((p1[1] + p2[1]) / 2)
            cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
            cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
            cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)
            dx = cx - XCenter
            dy = cy - YCenter
            cv2.putText(img_note, f"({dx}, {dy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
            cv2.line(img_note, (320, 240), (cx, cy), (255, 0, 0), 2)
            # cv2.line(img_note, (0, 240), (640, 240), (255, 0, 0), 2)
            # cv2.line(img_note, (320, 0), (320, 480), (255, 0, 0), 2)
            # pl =
            # cv2.line(img_note, )
            # cv2.putText(img_note, f"({}, {})")
        cv2.imshow("img_note ", img_note)
        cv2.waitKey(1)

    # img = cv2.imread(img_path)
    # cv2.imshow("src", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # img_bgr = precondition(img)
    # cv2.imshow("precondition", img_bgr)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    # cv2.imshow("img_hsv", img_hsv)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # mask = cv2.inRange(img_hsv, blueThreshold[0], blueThreshold[1])
    # cv2.imshow("mask", mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # mask = cv2.medianBlur(mask, 3)
    # cv2.imshow("maskAfterMedianBlur", mask)
    # cv2.waitKey(0)
    #
    # bbox = mask_find_b_boxs(mask)
    # most_credible_box = get_the_most_credible_box(bbox)
    #
    # p1 = tuple([most_credible_box[0], most_credible_box[1]])
    # p2 = tuple([most_credible_box[0] + most_credible_box[2], most_credible_box[1] + most_credible_box[3]])
    # cx = int((p1[0] + p2[0]) / 2)
    # cy = int((p1[1] + p2[1]) / 2)
    # img_note = img.copy()
    # cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
    # cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
    # cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)
    # dx = cx - XCenter
    # dy = cy - YCenter
    # cv2.putText(img_note, f"({dx}, {dy})", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
    # cv2.line(img_note, (0, 240), (640, 240), (255, 0, 0), 2)
    # cv2.line(img_note, (320, 0), (320, 480), (255, 0, 0), 2)
    # # pl =
    # # cv2.line(img_note, )
    # # cv2.putText(img_note, f"({}, {})")
    # cv2.imshow("img_note ", img_note)
    #
    # # print('(dx, dy): ', tuple([dx, dy]))
    # # with open("distance.txt", "a+") as file:
    # #     result = "height=150mm, radius="+str(most_credible_box[2])+"or"+str(most_credible_box[3])+", even="+str((most_credible_box[2]+most_credible_box[3])/2)+"\n"
    # #     print(result)
    # #     file.write(result)
    # cv2.waitKey(0)
