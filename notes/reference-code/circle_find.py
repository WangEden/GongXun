# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 21:35:39 2023

@author: sls
"""
import time
import picamera
import numpy as np
import cv2
from vision import *
def find_circle():
    
    img_flag = cv2.imread("2.jpg")
    img_morph = img_flag.copy()
    gray = cv2.cvtColor(img_flag, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(img_morph, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(img_morph, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            break
    cv2.imshow("output", np.hstack([img_flag, img_morph]))
#     print(x,y)
    cv2.waitKey(0)
if __name__ == '__main__':     
    try:
        print('1')
        setup()
        while 1:
#             tz1()
#             GPIO.output(38,GPIO.HIGH)
#             print(GPIO.output(38,GPIO.HIGH))
#             smdw()
#             sm()
#             yssb()
            pz(2)
            find_circle()
#             judge_color(2)
#             sm()
#             dwp(0)
#             tz22(1)
#             time.sleep(20)
#             sm()
            break
    except KeyboardInterrupt:
        print('1')