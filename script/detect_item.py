import cv2
import numpy as np
from xml.etree import ElementTree as ET

img_path = "10.jpg"
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
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(_mask, connectivity=8) # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


def get_the_most_credible_box(b_box):
    global XCenter, YCenter
    if len(b_box) == 0:
        return None
    if len(b_box) == 1:
        return b_box[0]
    sorted(b_box, key=lambda box: box[2] * box[3])
    sorted(b_box, key=lambda box: abs(box[0] + box[2] / 2 - XCenter))
    sorted(b_box, key=lambda box: abs(box[1] + box[3] / 2 - YCenter))
    return b_box[0]


if __name__ == '__main__':
    getColorThreshold(thresholdNode, 'red', redThreshold)
    getColorThreshold(thresholdNode, 'green', greenThreshold)
    getColorThreshold(thresholdNode, 'blue', blueThreshold)

    img = cv2.imread(img_path)
    cv2.imshow("src", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img_bgr = precondition(img)
    cv2.imshow("precondition", img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    cv2.imshow("img_hsv", img_hsv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    mask = cv2.inRange(img_hsv, blueThreshold[0], blueThreshold[1])
    cv2.imshow("mask", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    mask = cv2.medianBlur(mask, 3)
    cv2.imshow("maskAfterMedianBlur", mask)
    cv2.waitKey(0)

    bbox = mask_find_b_boxs(mask)
    most_credible_box = get_the_most_credible_box(bbox)

    p1 = tuple([most_credible_box[0], most_credible_box[1]])
    p2 = tuple([most_credible_box[0] + most_credible_box[2], most_credible_box[1] + most_credible_box[3]])
    cx = int((p1[0] + p2[0]) / 2)
    cy = int((p1[1] + p2[1]) / 2)
    img_note  = img.copy()
    cv2.rectangle(img_note, p1, p2, (255, 0, 0), 1)
    cv2.putText(img_note, f"({cx}, {cy})", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    cv2.circle(img_note, (cx, cy), 4, (64, 128, 255), -1)
    cv2.imshow("img_note ", img_note)
    dx = cx - XCenter
    dy = cy - YCenter
    print('(dx, dy): ', tuple([dx, dy]))
    cv2.waitKey(0)
