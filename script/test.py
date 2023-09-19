import cv2
import numpy as np

cameraTop = "/dev/cameraTop"
cameraInc = "/dev/cameraInc"

w = 480
h = 640

cap = cv2.VideoCapture(cameraTop)
cap.set(3, w)
cap.set(4, h)
cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))

# print("宽度：", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# print("高度：", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print("编码：", cap.get(cv2.CAP_PROP_FOURCC))

filename = "./output.mp4"

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(filename, fourcc, 30.0, (h, w))

srcPoint = np.uint8([[0, h], [0, 0], [w, 0]])
desPoint = np.uint8([[0, 0], [h, 0], [h, w]])

M = cv2.getAffineTransform(srcPoint, desPoint)
pad = np.zeros((2 * h, h, 3), dtype=np.uint8)

ret, frame = cap.read()

# print(pad.shape)
mask1, mask2 = None

# if ret:
#     mask1 = np.zeros(frame.shape[0:2], dtype=np.uint8)
#     mask2 = np.zeros(frame.shape[0:2], dtype=np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    srcImg = cv2.resize(frame, (2 * h, h))
    desImg = cv2.warpAffine(frame, M, (h, w))
    desImg = cv2.resize(desImg, (2 * h, h))

    cv2.imshow("srcImg", srcImg)
    cv2.imshow("desImg", desImg)

    cv2.waitKey(0)
    # mask1 = cv2.

    
