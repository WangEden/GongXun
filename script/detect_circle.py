import cv2
import numpy as np

test_file = '../static/videos/ring/1.mp4'
#cap = cv2.VideoCapture(test_file)
circle_center_points = []
camera = '/dev/video0'
cap = cv2.VideoCapture(camera)
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))


def calc_the_most_frequent_position_of_points(points):
    pass


try:
    while True:
        ret, frame = cap.read()                 
        img_note = frame.copy()
        img_calc = frame.copy()

        # 高斯滤波平滑
        img_calc = cv2.GaussianBlur(img_calc, (5, 5), 0)
        img_gray = cv2.cvtColor(img_calc, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray", img_gray)

        # 二值化
        binary = cv2.adaptiveThreshold(~img_gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10)
        erode_kernel = np.ones((1, 1), dtype=np.uint8)
        erosion_binary = cv2.erode(binary, kernel=erode_kernel, iterations=1)

        # 拓展图片维度
        erosion_binary_channel3 = np.repeat(erosion_binary[:, :, np.newaxis], repeats=3, axis=2)

        #print(erosion_binary_channel3.shape)
        #cv2.imshow("binary", erosion_binary_channel3)

        text = None
        # 在二值化画面中查找圆形
        circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)
        if circles is not None:
            circles = np.round(circles[0, :]).astype('int')
            for (x, y, r) in circles:
                text = "position("+str(x)+", "+str(y)+")"
                cv2.circle(img_note, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(img_note, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                # break

        cv2.putText(img_note, text, (5,5), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        cv2.imshow("output", np.hstack([erosion_binary_channel3, img_note]))
        cv2.waitKey(1)

except KeyboardInterrupt:
    print('end')
