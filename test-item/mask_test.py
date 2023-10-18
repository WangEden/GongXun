import cv2
import numpy as np

img = cv2.imread("img.png")
img_note = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
mask_ = cv2.bitwise_and(gray, gray)
cv2.imshow("mask_", mask_)
cv2.waitKey(0)


def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(
        _mask, connectivity=8
    )  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


b_box = mask_find_b_boxs(mask_)
b_box = sorted(b_box, key=lambda box: box[4], reverse=True)
box = b_box[0]

p1 = tuple([box[0] + 2, box[1] + 2])
p2 = tuple([box[0] + box[2] - 2, box[1] + box[3] - 2])

img2 = np.zeros(img.shape, dtype=np.uint8)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
cv2.rectangle(img2, p1, p2, (255, 255, 255), 5)
cv2.imshow("img2", img2)
cv2.waitKey(0)
# mask2 = cv2.bitwise_and(img2, img2)
mask = cv2.bitwise_and(mask_, img2)



cv2.imshow("mask", mask)
cv2.waitKey(0)
# src = np.zeros((480, 640), dtype=np.uint8)
# src2 = np.zeros((480, 640), dtype=np.uint8)
#
# binary = cv2.circle(src, (200, 200), 50, (255, 255, 255), -1)
# binary2 = cv2.circle(src2, (500, 200), 50, (255, 255, 255), -1)
#
# mask1 = cv2.bitwise_and(binary, binary)
# mask2 = cv2.bitwise_and(binary2, binary2)
# cv2.imshow("mask1", mask1)
# cv2.imshow("mask2", mask2)
# cv2.waitKey(0)
#
# mask = mask1 + mask2
# cv2.imshow("mask", mask)
# cv2.waitKey(0)
