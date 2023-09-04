import RPi.GPIO as GPIO
import picamera
import time
import cv2
import cv2 as cv
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar
from chassis import *
from arm import *
from color import *
from bjdj import *
# from ym import *
z=[0,0,0,0,0,0]
zx=[325,329.5,329.5,329]#312
zy=[236,245.5,245.5,245]#169
global tt
global x
global y
global xx
global area
xx=0
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
#     GPIO.setup(36, GPIO.IN)
    
       
def sm():
    global tt
    tt=[]
    tp = "1.jpg"
    img = cv2.imread(tp) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pyzbar.decode(gray)
    if result == []: 
        print("二维码识别失败")
    else:
        for i in result:
            tt=i.data.decode("utf-8")
        print('二维码识别成功')
        print(tt)
        width = 400
        height = 400
        img = np.ones((height, width, 4)) * (255, 255, 255, 0)
        text = tt
        cv2.putText(img, text, (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 10)
        cv.imwrite("image.jpg", img);
        img=Image.open('image.jpg')
        img.show()
        num = ''.join([x for x in tt if x.isdigit()])
        print(num)
        for i in range (0, 6) :
            z[5-i] = int (num) // (10 ** i) % 10            
        print(z)
        return tt
def pz(k):
    GPIO.output(7,GPIO.HIGH)
    cap = cv2.VideoCapture("/dev/main_video") 
    print(cap.set(3,640))
    cap.set(4,480)
    cap.set(cv2.CAP_PROP_AUTO_WB,1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,1)
    cap.set(cv2.CAP_PROP_EXPOSURE,7)
    ret, frame = cap.read()
    kernel = np.ones((3,3),np.float32)/9
    frame=cv.filter2D(frame,-1,kernel)
    resized_frame = cv2.resize(frame, (640, 480))
    cv2.imwrite(str(k)+".jpg", resized_frame)
    GPIO.output(7,GPIO.LOW)
    print("save success!")
    cap.release()
def pz1(k):
    cap = cv2.VideoCapture("/dev/sm_video") 
    print(cap.set(3,640))
    cap.set(4,480)
    cap.set(cv2.CAP_PROP_AUTO_WB,1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,1)
    cap.set(cv2.CAP_PROP_EXPOSURE,7)
    ret, frame = cap.read()
    kernel = np.ones((3,3),np.float32)/9
    frame=cv.filter2D(frame,-1,kernel)
    resized_frame = cv2.resize(frame, (640, 480))
    cv2.imwrite(str(k)+".jpg", resized_frame)
    print("save success!")
    cap.release()
def gd():
    GPIO.output(7,GPIO.LOW)       
def dwp(a):
    global x
    global y
    global xx
    global area
    img_bgr = cv2.imread('2.jpg')
#     img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
#     l_channel, a_channel, b_channel = cv2.split(img_lab)
#     clahe = cv2.createCLAHE(clipLimit = 1.5 , tileGridSize=(1,1))
#     a_channel = clahe.apply(a_channel)
#     b_channel = clahe.apply(b_channel)
#     l_channel = clahe.apply(l_channel)
#     img_lab = cv2.merge((l_channel, a_channel, b_channel))
#     img_bgr = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)
    #     size = img_bgr.shape
    #     print(size)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    if a == 1:
        thresh1 = np.array([160, 0, 135])
        thresh2 = np.array([255, 255, 255])
        thresh3 = np.array([0, 46, 135])
        thresh4 = np.array([20, 240, 240])
    elif a == 2:
        thresh1 = np.array([60, 15, 125])
        thresh2 = np.array([100 , 255, 255])
    elif a == 3:
        thresh1 = np.array([105,20, 46])
        thresh2 = np.array([140, 255, 255])
    elif a == 0:
        thresh1 = np.array([82,0,185])
        thresh2 = np.array([255,50,240])
    elif a == 4:
        thresh1 = np.array([80,0,180])
        thresh2 = np.array([255,100,255])
        
    elif a == 5:
        thresh1 = np.array([175, 0, 150])
        thresh2 = np.array([255, 255, 255])
        thresh3 = np.array([0, 46, 135])
        thresh4 = np.array([20, 240, 240])
    elif a == 6:
        thresh1 = np.array([60, 15, 125])
        thresh2 = np.array([78 , 255, 255])
    elif a == 7:
        thresh1 = np.array([105,25, 46])
        thresh2 = np.array([115, 255, 255])
#     if a == 0:
#         img_flag = cv2.inRange(res, thresh1, thresh2)
#     else:    
    img_flag = cv2.inRange(img_hsv, thresh1, thresh2)
    if a == 1 or a == 5:
#         
        img_flag2 =cv2.inRange(img_hsv, thresh3, thresh4)
        img_flag3 = cv2.bitwise_or(img_flag,img_flag2)
        dst = img_flag3.copy()
        img_morph = img_flag3.copy()
    else:
        dst = img_flag.copy()
        img_morph = img_flag.copy()
    if a == 0:
        h,w,c = img_hsv.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        x_data = np.array([140,140, 180,140,140,200,320,440,500,500,460,500,500,440,320,200]) 
        y_data = np.array([450,400, 315,230,180,180,200,180,180,230,315,400,450,450,430,450])-100 
        pts=np.c_[x_data, y_data]
        # print(pts)
        cv2.fillPoly(mask,[pts], (100), 8, 0)
        img_morph = cv2.bitwise_and(img_morph, img_morph, mask=mask)
        cv2.erode(img_morph, (3,3), img_morph, iterations= 1)
        cv2.dilate(img_morph, (3,3), img_morph, iterations= 3)
    elif a == 4:
       

#         cv2.erode(img_morph, (3,3), img_morph, iterations= 3)
        cv2.dilate(img_morph, (3,3), img_morph, iterations= 5)
    elif a == 5 or a==6 or a==7:
        print('666')
        h,w,c = img_hsv.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        x_data = np.array([140, 140, 480,480]) 
        y_data = np.array([500, 190, 190,500])-100 
        pts=np.c_[x_data, y_data]
        # print(pts)
        cv2.fillPoly(mask,[pts], (100), 8, 0)
        img_morph = cv2.bitwise_and(img_morph, img_morph, mask=mask)
        cv2.erode(img_morph, (3,3), img_morph, iterations= 5)
        cv2.dilate(img_morph, (3,3), img_morph, iterations= 5)
    else:
        h,w,c = img_hsv.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        x_data = np.array([140, 140, 480,480]) 
        y_data = np.array([500, 190, 190,500])-100 
        pts=np.c_[x_data, y_data]
        cv2.fillPoly(mask,[pts], (100), 8, 0)
        img_morph = cv2.bitwise_and(img_morph, img_morph, mask=mask)
        cv2.erode(img_morph, (3,3),img_morph , iterations= 1)
        cv2.dilate(img_morph, (3,3),img_morph, iterations= 3)
    cnts, _ = cv2.findContours(img_morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    cnts_sort = sorted(cnts, key= cv2.contourArea, reverse= True) 
    
    
    (u,v),radius = cv2.minEnclosingCircle(cnts_sort[0])
    area = np.pi * radius ** 2
    print(u,v,radius)
    print(area)

    box = cv2.minAreaRect(cnts_sort[0])
    points = np.int0(cv2.boxPoints(box))
#     cen_v = (points[0,0] + points[2,0]) / 2   
#     cen_h = (points[0,1] + points[2,1]) / 2    

    cen_b = (points[0,0] - points[2,0])
    cen_b = cen_b/abs(cen_b)
    if  cen_b==-1:
        cen_x1 = (points[0,1] )   
        cen_y1 = (points[3,1] )
        xx=abs(cen_x1-cen_y1)*-1
        if xx>-5:
            xx=0
    if  cen_b==1:
        cen_x2 = (points[0,1] )  
        cen_y2 = (points[1,1] )
        xx=abs(cen_x2-cen_y2)
        if xx <5:
            xx=0
    rows, cols = img_bgr.shape[:2]
    x=u
    y=v
    
#     print(x,y)
    if a == 4:
        dst=cv2.drawContours(img_bgr, [points], -1, (0,0,255), 5)
    else:
        dst = cv.circle(img_bgr, (int(u), int(v)), int(radius), (0, 0, 255), 5)
#     print(u,v,radius)
#     cv2.imshow('1.jpg', img_bgr)
#     cv2.imshow('2.jpg', img_flag)
#     cv2.imshow('2.jpg', img_morph)
    cv.imshow("dst", dst)
#     cv2.imshow('xin', res)
    cv2.waitKey(500)
#     cv2.waitKey(1000)
#     cv2.waitKey(0)
    cv2.destroyAllWindows()
#     ser.flushInput()
#     ser.close()
def tz(a):
    global x
    global y
    global xx
    global area
    if a == 0:  #zhuanpan
        while 1:
            aa=0
            while aa <1: 
#             time.sleep(0.2)
                pz(2)
                dwp(0)
                if area <110000 and area >60000:    
                    y=y-zy[0]
                    aa+=1
                    print(y)
#             print(zy[0])
            
            if y>20:
                print(y)
                move(6,y*1,100)
                
            elif y<-20:
                print(y)
                move(5,y*-1,100)
            elif y<20 and y>-20:
                print('finishy')
                break
        while 1 :
            aa=0
            while aa <1: 
                pz(2)
                dwp(0)
                if area <110000 and area >80000:    
                    x=x-zx[0]
                    aa+=1
                    print(x)

            if x>10:
                print(x)
                move(7,x*0.8,100)
            elif x<-10:
                print(x)
                move(8,x*-0.8,100)
            elif x<10 and x>-10:
                print('finishx')
                break
        while 1:
            aa=0
            while aa <1: 
                pz(2)
                dwp(0)
                if area <110000 and area >80000:    
                    y=y-zy[0]
                    aa+=1
                    print(y)
            if y>10:
                print(y)
                move(6,y*0.7,100)
                
            elif y<-10:
                print(y)
                move(5,y*-0.7,100)
            elif y<10 and y>-10:
                print('finishy')
                break
    if a == 1 or a ==2 or a == 3: 
        while 1:
            aa=0
            while aa <1: 
#             time.sleep(0.2)
                pz(2)
                dwp(a)
                if area <60000 and area >40000:    
                    y=y-zy[1]
                    aa+=1
                    print(y)
            if y>3:
                print(y)
                move(6,y*0.7,100) 
            elif y<-3:
                print(y)
                move(5,y*-0.7,100)
            elif y<3 and y>-3:
                print('finishy')
                break
        while 1 :
            aa=0
            while aa <1: 
                pz(2)
                dwp(a)
                if area <60000 and area >40000:    
                    x=x-zx[1]
                    aa+=1
                    print(x)
            if x>3:
                print(x)
                move(7,x*0.7,100)
            elif x<-3:
                print(x)
                move(8,x*-0.7,100)
            elif x<3 and x>-3:
                print('finishx')
                break
    if a == 4:#jiagong
#         dzdw()
#         dzystz()
        pz(2)
        dwp(4)
        while xx!=0:
            while xx>0:
                time.sleep(0.2)
                print(xx)
                move(10,xx*0.5,100)
                pz(2)
                dwp(4)
            while xx<0:
                time.sleep(0.2)
                print(xx)
                move(9,xx*-0.5,100)
                pz(2)
                dwp(4)
        print('finish')
    if a == 5 or a ==6 or a ==7:
        while 1:
            aa=0
            while aa <1: 
                pz(2)
                dwp(a-4)
                if area <60000 and area >40000:    
                    y=y-zy[2]
                    aa+=1
                    print(y)
            
            if a == 5:
                print(y)
            if y>10:
                print(y)
                move(6,y*1,100) 
            elif y<-15:
                print(y)
                move(5,y*-0.7,100)
            elif y<15 and y>-15:
                print('finishy')
                break
        while 1 :
            aa=0
            while aa <1: 
                pz(2)
                dwp(a-4)
                if area <60000 and area >40000:    
                    x=x-zx[2]
                    aa+=1
                    print(x)
            
            if x>15:
                print(x)
                move(7,x*0.7,100)
            elif x<-15:
                print(x)
                move(8,x*-0.7,100)
            elif x<15 and x>-15:
                print('finishx')
                break
    if a == 8 or a ==9 or a ==10:
        while 1:
            aa=0
            while aa <1: 
                pz(2)
                dwp(a-3)
                if area <20000 and area >10000:    
                    y=y-zy[3]
                    aa+=1
                    print(y)
            
            if a == 8:
                print(y)
            if y>8:
                print(y)
                move(6,y*0.6,100) 
            elif y<-8:
                print(y)
                move(5,y*-0.6,100)
            elif y<8 and y>-8:
                print('finishy')
                break
        while 1 :
            aa=0
            while aa <1: 
                pz(2)
                dwp(a-3)
                if area <20000 and area >10000:    
                    x=x-zx[3]
                    aa+=1
                    print(x)
            
            if x>8:
                print(x)
                move(7,x*0.6,100)
            elif x<-8:
                print(x)
                move(8,x*-0.6,100)
            elif x<8 and x>-8:
                print('finishx')
                break
def smdw() :
    global tt
    ab=65
    dzp()
    pz(1)
    time.sleep(0.2)
    sm()
    while tt == []:
        ab=ab+2
        kk(3,ab)
        time.sleep(0.2)
        pz(1)
        time.sleep(0.2)
        sm()
        if tt == []:
            kk(3,85)
            time.sleep(0.2)
            pz(1)
            time.sleep(0.2)
            sm()
    fwp()
            
def yssb(a):
    dzys2()
    if a == 1:
        i=0
        while i < 3:
            pz(3)
            judge_color(3)
            if judge_color(3) == z[i] :
                time.sleep(0.4)
                if i == 0:
                    time.sleep(3)
                pz(3)
                judge_color(3)
                if judge_color(3) == z[i] :
                    zp(i+1)
                    zhua2()
                    
                    i+=1

        zp(4)
        time.sleep(0.3)
        pz(10)
        fwzhua2()
        time.sleep(0.5)
#         fwdw()
    if a == 2:
        i=3
        while i < 6:
            pz(3)
            judge_color(3)
            if judge_color(3) == z[i] :
                time.sleep(0.4)
                if i == 3:
                    time.sleep(3)
                pz(3)
                judge_color(3)
                if judge_color(3) == z[i] :
                    zp(i-2)
                    zhua2()
                    i+=1
        zp(4)
        time.sleep(0.3)
        pz(10)
        fwzhua2()
        time.sleep(0.5)
def step3(a):
    
    print('step3')
    move(7,300,15)
    if a == 1:
        if z[0]==2:
            move(5,1180,15)
        elif z[0]==1:
            move(5,900,15)
        elif z[0]==3:
            move(5,1460,15)

    if a == 1:
        cs=z[0]
        move1(9,490,30)
        dzdw2()
        tz(4)
        i=0
        while i<3:
            if z[i]-cs==0:
                print('db')
            elif z[i]-cs==-1:
                move(8,210,15)
                print('db')
            elif z[i]-cs==1:
                move(7,210,15)
            elif z[i]-cs==-2:
                move(8,420,15)
                print('db')
            elif z[i]-cs==2:
                move(7,420,15)
            cs=z[i]
            i+=1
#             if i == 1:
#                 dzdwys()
            tz(4)
            tz(cs)
            na1(i)
            dzdw22()
        i=0
        while i<3:
#             zp(i+1)
            if z[i]-cs==0:
#                 ndb()
                print('ndb')
            elif z[i]-cs==-1:
                move(8,210,15)
#                 ndb()
#                 print('ndb')
            elif z[i]-cs==1:
                move(7,210,15)
#                 ndb()
            elif z[i]-cs==-2:
                move(8,420,15)
#                 ndb()
#                 print('ndb')
            elif z[i]-cs==2:
                move(7,420,15)
            cs=z[i]
            tz(4)
            tz(cs+4)
            ndb1(i+1)
            i+=1
        zp(4)
        tz(4)
        fwna()
    if a == 2:
        if z[3]==2:
            move(5,1180,15)
        elif z[3]==1:
            move(5,900,15)
        elif z[3]==3:
            move(5,1460,15)

    if a == 2:
        cs=z[3]
        move1(9,490,30)
        dzdw2()
        tz(4)
        i=3
        while i<6:
            if z[i]-cs==0:
                print('db')
            elif z[i]-cs==-1:
                move(8,210,15)
                print('db')
            elif z[i]-cs==1:
                move(7,210,15)
            elif z[i]-cs==-2:
                move(8,420,15)
                print('db')
            elif z[i]-cs==2:
                move(7,420,15)
            cs=z[i]
            i+=1
#             if i == 1:
#                 dzdwys()
            tz(4)
            tz(cs)
            na1(i-3)
            dzdw22()
        i=3
        while i<6:
#             zp(i+1)
            if z[i]-cs==0:
#                 ndb()
                print('ndb')
            elif z[i]-cs==-1:
                move(8,210,15)
#                 ndb()
#                 print('ndb')
            elif z[i]-cs==1:
                move(7,210,15)
#                 ndb()
            elif z[i]-cs==-2:
                move(8,420,15)
#                 ndb()
#                 print('ndb')
            elif z[i]-cs==2:
                move(7,420,15)
            cs=z[i]
            tz(4)
            tz(cs+4)
            ndb1(i-2)
            i+=1
        zp(4)
        tz(4)
        fwna()
def step4(a):
    print('step4')
    if a == 1:
        if z[2]==2:
            move(7,900,15)
        elif z[2]==1:
            move(7,1100,15)
        elif z[2]==3:
            move(7,730,15)
    if a == 1:
        if z[0]==2:
            move(5,1100,15)
        elif z[0]==1:
            move(5,895,15)
        elif z[0]==3:
            move(5,1320,15)
    if a == 1:
        cs=z[0]
        move1(9,490,30)
        dzdw2()
        tz(4)
        i=0
        while i<3:
            if z[i]-cs==0:
                print('db')
            elif z[i]-cs==-1:
                move(8,210,15)
                print('db')
            elif z[i]-cs==1:
                move(7,210,15)
            elif z[i]-cs==-2:
                move(8,420,15)
                print('db')
            elif z[i]-cs==2:
                move(7,420,15)
            cs=z[i]
            i+=1
            tz(4)
            tz(cs)
            na1(i)
            dzdw22()
        zp(4)
        tz(4)
        fwna()
    if a == 2:
        if z[5]==2:
            move(7,900,15)
        elif z[5]==1:
            move(7,1100,15)
        elif z[5]==3:
            move(7,730,15)
    if a == 2:
        if z[3]==2:
            move(5,1100,15)
        elif z[3]==1:
            move(5,895,15)
        elif z[3]==3:
            move(5,1320,15)
    if a == 2:
        cs=z[3]
        move1(9,490,30)
        dzdw2()
        tz(4)
        i=3
        while i<6:
            if z[i]-cs==0:
                print('db')
            elif z[i]-cs==-1:
                move(8,210,30)
                print('db')
            elif z[i]-cs==1:
                move(7,210,30)
            elif z[i]-cs==-2:
                move(8,420,30)
                print('db')
            elif z[i]-cs==2:
                move(7,420,30)
            cs=z[i]
            i+=1
            tz(4)
            tz(cs+7)
            die(i-3)
            dzdw22()
        zp(4)
        tz(4)
        fwna()
#         i=0        
def step5():
    print('step5')
    if z[2]==2:
        move(8,900,20)
    elif z[2]==1:
        move(8,1100,20)
    elif z[2]==3:
        move(8,730,20)
    move(5,2000,15)
    move1(9,980,30)
    dzdw()
    time.sleep(0.5)
    move(8,80,20)
def step6():
    if z[5]==1:
        move(7,1600,15)
    elif z[5]==2:
        move(7,1400,15)
    elif z[5]==3:
        move(7,1200,15)
    move(6,600,15)
if __name__ == '__main__':     
    try:
        setup()
        setupbjdj()
#         start()
        while 1:
#             tz(2)
#             step4(1)
#             step5(1)
            print('1')
#             print(zx[1])
#             tz(0)
#             step3(1)
#             yssb(1)
#             pz(2)
            dwp(4)
#             tz(8)
#             GPIO.output(38,GPIO.HIGH)
#             print(GPIO.output(38,GPIO.HIGH))
#             smdw()
#             sm()
#             yssb()
#             pz(2)
#             judge_color(2)
#             sm()
#             dwp(0)
#             tz22(1)
#             time.sleep(20)
#             sm()
            break
    except KeyboardInterrupt:
        GPIO.cleanup()
        