import cv2
import numpy as np
def ym():
    
    img = cv2.imread("2.jpg")
    hsv = cv2.cvtColor(img, code=cv2.COLOR_BGR2HSV)
#     size=img.shape
#     print(size)
    h,w,c = img.shape
    mask = np.zeros((h, w), dtype=np.uint8)
#     x_data = np.array([80, 90, 120,115,145, 130,145,115 ,125, 90, 80]+[560,550,520,525,495,510,495,525,520,550,560]) 
#     y_data = np.array([320, 280, 250,280,280, 320,360,360, 390, 360, 320]+[320, 280, 250,280,280, 320,360,360, 390, 360, 320])-100 
#     pts=np.c_[x_data, y_data]
    x_data = np.array([140, 140, 480,480]) 
    y_data = np.array([500, 190, 190,500])-100 
    pts=np.c_[x_data, y_data]
#     # print(pts)
    cv2.fillPoly(mask,[pts], (255), 8, 0)
    res = cv2.bitwise_not(img, img, mask=mask)
    cv2.imshow("mask",mask)
    cv2.imshow('xin', img)
    cv2.waitKey(0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
ym()