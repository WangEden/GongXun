import cv2
import numpy as np


def mask_find_b_boxs(_mask):
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(
        _mask, connectivity=8
    )  # connectivity参数的默认值为8
    stats = stats[stats[:, 4].argsort()]
    return stats[:-1]


img = np.zeros((480, 640), dtype=np.uint8)
img2 = np.zeros((480, 640), dtype=np.uint8)
cv2.imshow("bin", img)
cv2.waitKey(0)

binary = cv2.circle(img, (200, 200), 50, (255, 255, 255), -1)
cv2.imshow("bin", img)
cv2.waitKey(0)
# binary2 = cv2.circle(img2, (210, 200), 50, (255, 255, 255), -1)
# cv2.imshow("bin", binary)
# cv2.waitKey(0)
#
# cv2.imshow("bin2", binary2)
# cv2.waitKey(0)
#
# bitWiseXor = cv2.bitwise_xor(binary, binary2)
# cv2.imshow("bitWiseAnd", bitWiseXor)
# cv2.waitKey(0)

bitAnd = cv2.bitwise_and(binary, binary)
cv2.imshow("csc", bitAnd)
cv2.waitKey(0)

b_box = mask_find_b_boxs(bitAnd)
print(b_box)

print(bitAnd.shape)
