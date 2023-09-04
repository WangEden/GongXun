import cv2
import numpy as np

test_file = './test/4.mp4'
cap = cv2.VideoCapture(test_file)
circle_center_points = []

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

        print(erosion_binary_channel3.shape)
        cv2.imshow("binary", erosion_binary_channel3)

        # 在二值化画面中查找圆形
        circles = cv2.HoughCircles(erosion_binary, cv2.HOUGH_GRADIENT, 1, 100)
        if circles is not None:
            circles = np.round(circles[0, :]).astype('int')
            for (x, y, r) in circles:
                cv2.circle(img_note, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(img_note, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                # break

        cv2.imshow("output", np.hstack([frame, erosion_binary_channel3, img_note]))
        cv2.waitKey(0)

except KeyboardInterrupt:
    print('end')