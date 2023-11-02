from jetcam.csi_camera import CSICamera
import cv2
import numpy as np
import serial
import  struct

#串口
com = serial.Serial("/dev/ttyTHS1",115200)



# 色环抓取标志位    1 for red  2 for grren 3 for blue  
blob_flag=1
blob_target_list=[]
#串口接收标志位
uartres=0
uartfin=0
#颜色抓取标志位
color_grab_flag=1
target_list=[]
#白色转盘标志位
plate_flag=1
plate_target_list=[]
#创建二维码检测器
qrDecoder = cv2.QRCodeDetector()

#二维码检测任务标志位
QR_flag=1

#三种颜色的物料的BGR值,以及换算出的HSV值 1：红色  2：绿色  3：蓝色
BGR1=[47,41,122]
BGR2=[60,86,22]
BGR3=[98,65,39]
color1= np.uint8([[[BGR1[0], BGR1[1], BGR1[2]]]])
color2= np.uint8([[[BGR2[0], BGR2[1], BGR2[2]]]])
color3= np.uint8([[[BGR3[0], BGR3[1], BGR3[2]]]])
hsv1= cv2.cvtColor(color1, cv2.COLOR_BGR2HSV)
hsv2= cv2.cvtColor(color2, cv2.COLOR_BGR2HSV)
hsv3= cv2.cvtColor(color3, cv2.COLOR_BGR2HSV)
#红色色环上下限，
blob1_low=np.array([hsv1[0][0][0]-10,60,45],dtype=np.uint8)
blob1_high=np.array([hsv1[0][0][0]+10,255,255],dtype=np.uint8)
#绿色色环上下限
blob2_low=np.array([hsv2[0][0][0]-10,60,50],dtype=np.uint8)
blob2_high=np.array([hsv2[0][0][0]+10,255,255],dtype=np.uint8)
#蓝色色环上下限_
blob3_low=np.array([105,150,50],dtype=np.uint8)
blob3_high=np.array([115,190,255],dtype=np.uint8)

#红色上下限，
hsv1_low=np.array([hsv1[0][0][0]-12,80,45],dtype=np.uint8)
hsv1_high=np.array([hsv1[0][0][0]+12,255,255],dtype=np.uint8)
#绿色上下限
hsv2_low=np.array([hsv2[0][0][0]-10,90,55],dtype=np.uint8)
hsv2_high=np.array([hsv2[0][0][0]+10,240,255],dtype=np.uint8)
#蓝色上下限_
hsv3_low=np.array([hsv3[0][0][0]-10,80,50],dtype=np.uint8)
hsv3_high=np.array([hsv3[0][0][0]+10,255,255],dtype=np.uint8)
#白色转盘HSV上下限
hsv_white_low=np.array([105,10,180],dtype=np.uint8)
hsv_white_high=np.array([135,50,255],dtype=np.uint8)

#上位机向下位机发送步进微调指令
#控制位：0xA1
#数据位：0x00 停止              0x01 前进                0x02   后退              0x03 左行             0x04右行
def pack_stepmotor(a):
    temp = struct.pack("<BBBBB",0xBB,0xCC,0xA1,a,0xDD)
    print(temp)
    com.write(temp)

#上位机向下位机发送路线指令
#控制位：0xA2
#数据位：0x00原点    0x01扫描二维码   0x02圆盘  0x03粗加工 0x04精加工
def pack_routine(a):
    temp = struct.pack("<BBBBB",0xBB,0xCC,0xA2,a,0xDD)
    print(temp)

    com.write(temp)

#上位机向下位机发送舵机控制指令
#控制位：0xA3
#数据位：： 0x01～0x
def  pack_servo(a):
    temp = struct.pack("<BBBBB",0xBB,0xCC,0xA3,a,0xDD)
    print(temp)

    com.write(temp)
#串口接受
def unpack_state():
    receive=com.read(2)
    print(receive)

    return receive

#定义一个形态学处理的函数
def good_thresh_img(img):
    gs_frame = cv2.GaussianBlur(img, (5, 5), 0)                     #高斯滤波
    hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)                 # 转化成HSV图像
    erode_hsv = cv2.erode(hsv, None, iterations=2)
    return erode_hsv

#寻找边界
def extract_contour(img):
    contours,hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    return contours

#用矩形框框出色环
def blob_find_target(contours,draw_img):
    global blob_target_list
    for c in contours:
        if cv2.contourArea(c) < 3000:             #过滤掉较面积小的物体
            continue
        else:
            blob_target_list.append(c)               #将面积较大的物体视为目标并存入目标列表
    for i in blob_target_list:                       #绘制目标外接矩形
        rect = cv2.minAreaRect(i)
        box = cv2.boxPoints(rect)
        cv2.drawContours(draw_img, [np.int0(box)], -1, (0, 255, 255), 2)
    return draw_img

#用矩形框框出圆盘
def plate_find_target(contours,draw_img):
    global plate_target_list
    for c in contours:
        if cv2.contourArea(c) < 3000:             #过滤掉较面积小的物体
            continue
        else:
            plate_target_list.append(c)               #将面积较大的物体视为目标并存入目标列表
    for i in plate_target_list:                       #绘制目标外接矩形
        rect = cv2.minAreaRect(i)
        box = cv2.boxPoints(rect)
        cv2.drawContours(draw_img, [np.int0(box)], -1, (0, 255, 255), 2)
    return draw_img
#用矩形框框出色块
def find_target(contours,draw_img):
    for c in contours:
        if cv2.contourArea(c) < 4500:             #过滤掉较面积小的物体
            continue
        else:
            target_list.append(c)               #将面积较大的物体视为目标并存入目标列表
    for i in target_list:                       #绘制目标外接矩形
        rect = cv2.minAreaRect(i)
        box = cv2.boxPoints(rect)
        cv2.drawContours(draw_img, [np.int0(box)], -1, (0, 255, 255), 2)
    return draw_img

#画出中心点坐标
def draw_center(target_list,draw_img):
    for c in target_list:
        M = cv2.moments(c)                   #计算中心点的x、y坐标
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        print('center_x:',center_x)
        print('center_y:',center_y)
        cv2.circle(draw_img,(center_x,center_y),7,128,-1)#绘制中心点
        str1 = '(' + str(center_x)+ ',' +str(center_y) +')' #把坐标转化为字符串
        cv2.putText(draw_img,str1,(center_x-50,center_y+40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)#绘制坐标点位

#膨胀函数的内核
kernel = np.ones((4,4),np.uint8)

#色环抓取函数
def blob_find(x):
    global blob_flag
    global blob_target_list
    camera = CSICamera(capture_device=0,width=480, height=360, capture_width=480, capture_height=360, capture_fps=30)
    image = camera.read()
    while blob_flag:
        image = camera.read()
        blob_target_list=[]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        if(x==1):
            mask = cv2.inRange(hsv, blob1_low, blob1_high)
        if(x==2):
            mask = cv2.inRange(hsv, blob2_low, blob2_high)
        if(x==3):
            mask = cv2.inRange(hsv, blob3_low, blob3_high)
        img_dilate = cv2.dilate(mask,kernel, iterations=4)
        contours=extract_contour(img_dilate)
        cv2.imshow("mask",mask)
        cv2.imshow("dilate",img_dilate)
        out=blob_find_target(contours,image)
        final_img = draw_center(blob_target_list,out)
        cv2.imshow("final",out)
        kk = cv2.waitKey(1)
        if kk == 27:  # 按下 exit 键，退出
            break

#色块抓取函数
def color_grab(x):
    global  color_grab_flag
    global target_list
    global uartfin,uartres
    uartfin=0
    uartres=0
    camera = CSICamera(capture_device=0,width=480, height=360, capture_width=480, capture_height=360, capture_fps=30)
    image = camera.read()
    while color_grab_flag:
        image = camera.read()
        target_list=[]
        hsv = good_thresh_img(image)
        if(x==1):
            mask = cv2.inRange(hsv, hsv1_low, hsv1_high)
        if(x==2):
            mask = cv2.inRange(hsv, hsv2_low, hsv2_high)
        if(x==3):
             mask = cv2.inRange(hsv, hsv3_low, hsv3_high)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        contours= extract_contour(mask)
        out=find_target(contours,image)
        final_img = draw_center(target_list,out)
        uartflag = unpack_state()
        if uartflag == 0xF0:
            uartres=1
        if uartres:
            if uartflag ==0x0F
                break

        elif target_list[0]&&target_list[1]:#中心在指定区域
            if x == 1:
                pack_servo(0x04)
            if x == 2:
                pack_servo(0x05)
            if x == 3:
                pack_servo(0x06)
        cv2.imshow("CSI Camera",mask)
        cv2.imshow("hsv",hsv)
        cv2.imshow("iamge",image)
        cv2.imshow("out",out)
        kk = cv2.waitKey(1)
        if kk == 27:  # 按下 exit 键，退出
            break

#二维码扫描任务函数
def Scan():
    global QR_flag
    global qrDecoder
    camera = CSICamera(capture_device=0,width=480, height=360, capture_width=480, capture_height=360, capture_fps=30)
    while QR_flag:
        image = camera.read()
        cv2.imshow("CSI Camera",image)
        data,bbox,rectifiedImage = qrDecoder.detectAndDecode(image)
        print(data)
        kk = cv2.waitKey(1)
        if kk == 27:  # 按下 exit 键，退出
            break
        else:
            if len(data)>0:
                QR_flag=0
                return data
            
def plate_find():
    global plate_flag
    global plate_target_list
    camera = CSICamera(capture_device=0,width=480, height=360, capture_width=480, capture_height=360, capture_fps=30)
    while QR_flag:
        image = camera.read()
        plate_target_list=[]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        ##中值滤波  图像平滑
        hsv = cv2.medianBlur(hsv, 7)
        mask = cv2.inRange(hsv, hsv_white_low, hsv_white_high)
        mask = cv2.dilate(mask, None, iterations=4)
        contours= extract_contour(mask)
        out=plate_find_target(contours,image)
        final_img = draw_center(plate_target_list,out)
        cv2.imshow("image",out)
        if plate_target_list[0]:
            pack_stepmotor()
        elif plate_target_list[0]:
            pack_stepmotor()
        elif plate_target_list[1]:
            pack_stepmotor()
        elif plate_target_list[1]:
            pack_stepmotor()
        else:
            pack_stepmotor(0x00)
        if unpack_state() == 0x0F:
            break
        kk = cv2.waitKey(1)
        if kk == 27:  # 按下 exit 键，退出
            break
while 1:
    if unpack_state() == 0xF0:
        break
    else pack_servo(0x01)#机械臂抬起扫描二维码
while 1:
    if unpack_state() == 0x0F:
        break
while 1:
    if unpack_state() == 0xF0:
        break
    else pack_routine(0x01)#原点出发原料区
while 1:
    if unpack_state() == 0x0F:
        break
while 1:
    if unpack_state() == 0xF0:
        break
    else pack_servo(0x02)#机械臂原料区判断
while 1:
    if unpack_state() == 0x0F:
        break
plate_find()
while 1:
    if unpack_state() == 0xF0:
        break
    else pack_servo(0x03)#机械臂原料区颜色
while 1:
    if unpack_state() == 0x0F:
        break
color_grab(1)
color_grab(2)
color_grab(3)
while 1:
    if unpack_state() == 0xF0:
        break
    else pack_routine(0x02)#原料区出发粗加工
while 1:
    if unpack_state() == 0x0F:
        break