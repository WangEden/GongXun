import sensor, image, time
from pyb import UART, LED
from math import pi as PI
from math import tan, sqrt


sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.VGA)    # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.
#sensor.set_brightness(6)   #设置亮度
#sensor.set_contrast(3) #对比度
#sensor.set_gainceiling(2)   #增益上限
#sensor.set_auto_gain(False,gain_db=-1) #增益
#sensor.set_auto_exposure(False,5000)  #曝光速度

# 串口初始化
uart = UART(3, 19200)
uart.init(19200, bits=8, parity=None, stop=1)
lastRecv = ''

def Send_Message(content):
    global sendState, uart
    uart.write(content)
    # if sendState:
    #     uart.write(content)
    #     sendState = False


def Recv_Message():
    global lastRecv
    s = ''
    response = uart.read()
    if response != None:
        s = str(response)[2:len(s)-1]
        index = s.find('!') # 返回第一个！的下标
        s = s[0:index]      # 只截取第一个！前的内容
        if lastRecv != s:
            lastRecv = s
        # print(response)
        print('recv: '+s)
        return s
    else:
        return ''


def FormatNumber(num:int):
    temp = num if num > 0 else -num
    if 0 <= num < 10:
        return '+0'+str(temp)
    if 10 <= num <= 20:
        return '+'+str(temp)
    if -10 < num < 0:
        return '-0'+str(temp)
    if -20 <= num <= -10:
        return '-'+str(temp)
    return '+99'


def FormatPoints(points):
    # print(points)
    resStr = ''
    for p in points:
        resStr += FormatNumber(p[0])
        resStr += FormatNumber(p[1])
    resStr += '\r'
    return resStr


def FormatPoint(point):
    # print(points)
    x, y = point
    resStr = ''
    resStr += FormatNumber(x)
    resStr += FormatNumber(y)
    resStr += '\r'
    return resStr


# 初始铅笔框区域信息
AreaData = {
    'dTop': 197, 'dBottom': 195, 'dLeft': 198, 'dRight': 206,
    'leftInclineAngle': 86.4, 'rightInclineAngle': 94.1,
}
# 区域坐标点
MapPoints = {
    'TopLeft': (109, 17), 'TopRight': (525, 17),
    'BottomLeft': (82, 452), 'BottomRight': (556, 452)
}
# 低分辨率下的初始铅笔框区域信息
AreaDataL = {
    'dTop': 48, 'dBottom': 54, 'dLeft': 50, 'dRight': 55,
    'leftInclineAngle': 86.4, 'rightInclineAngle': 94.1,
}
# 区域坐标点
MapPointsL = {
    'TopLeft': (26, 8), 'TopRight': (124, 8),
    'BottomLeft': (23, 113), 'BottomRight': (130, 113)
}

# 存储矩形面积
RectangleSize = (1488, 3200)
RectWidthSize = (27, 46)
RectHeightSize = (45, 65)

RedLightThreshold_Raw = (91, 100, -5, 9, 0, 15) # 初始红光阈值
RedLightInBlackThreshold_Raw = (91, 100, -5, 9, 0, 15) # 初始红光阈值
BlackLineThreshold_Raw = (5, 44, -26, 4, -10, 20) # 初始黑线阈值
RedLightThreshold_Real = ()

MainRoiArea = (94, 14, 406, 385)
MainRoiAreaL = (25, 6, 106, 105)

img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
canvaMono = sensor.alloc_extra_fb(640, 480, sensor.RGB565) # 要改大小
imgL = sensor.alloc_extra_fb(160, 120, sensor.RGB565)
canvaLMono = sensor.alloc_extra_fb(160, 120, sensor.RGB565) # 要改大小

# 高分辨率下的初始坐标
CenterBlockcX, CenterBlockcY = 28, 230
# 低分辨率下的初始坐标
CenterBlockcXL, CenterBlockcYL = round(CenterBlockcX * 0.25), round(CenterBlockcX * 0.25)

# 高分辨率下面积阈值
SizeThreshold = 20
# 低分辨率下面积阈值
SizeThresholdL = 5


# 找最大色块
def find_max_blob(blobs):
    if len(blobs) != 0:
        max_size=0
        for blob in blobs:
            if blob[2]*blob[3] > max_size:
                max_blob=blob
                max_size = blob[2]*blob[3]
        return max_blob
    return None


# 根据阈值返回一个方块的中心坐标
def GetBlockByBinary(threshold, sizeThreshold, mono):
    global img
    mono.clear()
    mono.draw_image(img, 0, 0)
    mono.binary([threshold])
    red_blobs = mono.find_blobs([(90, 100, -5, 5, -5, 5)], area_threshold=sizeThreshold, merge=True)
    red_blob = find_max_blob(red_blobs)
    if red_blob != None:
        center_block_cx = int(red_blob.cx())
        center_block_cy = int(red_blob.cy())
        # print(center_block_cx, center_block_cy)
        return center_block_cx, center_block_cy
    return tuple()


# 根据初始光点位置设置高分辨率坐标原点
def SetTheMapSourcePoint():
    global img, canvaMono, SizeThreshold
    red_blob = None
    while not red_blob:
        img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
        canvaMono.draw_image(img, 0, 0)
        canvaMono.binary([RedLightThreshold_Raw])
        red_blobs = canvaMono.find_blobs([(90, 100, -5, 5, -5, 5)], area_threshold=SizeThreshold, merge=True)
        red_blob = find_max_blob(red_blobs)
    center_block_cx = int(red_blob.cx())
    center_block_cy = int(red_blob.cy())
#    print(center_block_cx, center_block_cy)
    return center_block_cx, center_block_cy


# 根据五点激光设置铅笔框区域: 要用串口进行矫正
#def SetMapArea():
#    pass
# 根据五点激光修改区域信息


# 根据坐标原点建立边框
def BuildCoordinate(centerBlockX, centerBlockY, areaData):
    dT = areaData['dTop']
    dB = areaData['dBottom']
    dL = areaData['dLeft']
    dR = areaData['dRight']
    lIncAgl = areaData['leftInclineAngle']
    rIncAgl = areaData['rightInclineAngle']
    TopLeftX = int((centerBlockX - dL) + tan(((90 - lIncAgl) / 180 ) * PI))
    TopLeftY = int(centerBlockY - dT)
    TopLeft = tuple([TopLeftX, TopLeftY])
    TopRightX = int((centerBlockX + dR) + tan(((90 - rIncAgl) / 180 ) * PI))
    TopRightY = int(centerBlockY - dT)
    TopRight = tuple([TopRightX, TopRightY])
    BottomLeftX = int((centerBlockX - dL) - tan(((90 - lIncAgl) / 180 ) * PI))
    BottomLeftY = int(centerBlockY + dB)
    BottomLeft = tuple([BottomLeftX, BottomLeftY])
    BottomRightX = int((centerBlockX + dR) - tan(((90 - rIncAgl) / 180 ) * PI))
    BottomRightY = int(centerBlockY + dB)
    BottomRight = tuple([BottomRightX, BottomRightY])
    map_points = dict(TopLeft=TopLeft, TopRight=TopRight, BottomLeft=BottomLeft, BottomRight=BottomRight)
#    print(map_points)
    return map_points


# 先画出区域方便调试
def DrawMap(centerBlockCx, centerBlockCy, mapPoints):
    global img
    #img.draw_cross(centerBlockCx, centerBlockCy)
    img.draw_line(mapPoints['TopLeft'] + mapPoints['TopRight'], color=(0,0,255))
    img.draw_line(mapPoints['TopRight'] + mapPoints['BottomRight'], color=(0,0,255))
    img.draw_line(mapPoints['BottomRight'] + mapPoints['BottomLeft'], color=(0,0,255))
    img.draw_line(mapPoints['BottomLeft'] + mapPoints['TopLeft'], color=(0,0,255))


# 判断在哪个象限
# 2 | 1
# 3 | 4
def DetectQuadrant(x, y, cenBcX, cenBcY):
    dx = x - cenBcX
    dy = y - cenBcY
    if dx != 0 or dy != 0:
        quadrant = 0
        if dx < 0 and dy < 0:
            quadrant = 2
        elif dx > 0 and dy < 0:
            quadrant = 1
        elif dx < 0 and dy > 0:
            quadrant = 3
        elif dx > 0 and dy > 0:
            quadrant = 4
        return quadrant
    else:
        return 0


# 在一条直线上根据y获取x
def LineFromYGetX(y, LcenBcX, LcenBcY, incAgl):
    x = LcenBcX
    dy = LcenBcY - y
    dy = dy if dy > 0 else -dy
    x = LcenBcX + dy * tan((90 - incAgl) / 180 * PI) \
        if dy > 0 \
        else LcenBcX - dy * tan((90 - incAgl) / 180 * PI)
    return x


# 判断是否在区域内
def isInMainArea(x, y, centerBlockcX, centerBlockcY, areaData):
    flag = True
    if x > centerBlockcX:
        lineX = LineFromYGetX(y, centerBlockcX + areaData['dRight'], centerBlockcY, areaData['rightInclineAngle'])
        if x > lineX:
            flag = False
    else:
        lineX = LineFromYGetX(y, centerBlockcX - areaData['dLeft'], centerBlockcY, areaData['leftInclineAngle'])
        if x < lineX:
            flag = False
    if y > centerBlockcY + areaData['dBottom'] or y < centerBlockcY - areaData['dTop']:
        flag = False
    return flag


# 计算色块的图上坐标: -20 -> 20, -20 -> 20
def GetBlockXYinMap(x, y, centerBlockcX, centerBlockcY, areaData):
    if not isInMainArea(x, y, centerBlockcX, centerBlockcY, areaData):
        return tuple()
    quadrant = DetectQuadrant(x, y, centerBlockcX, centerBlockcY)
    resX, resY = 0, 0
    if quadrant != 0: # 待验证和简化
        if quadrant == 1:
            lineX = LineFromYGetX(y, centerBlockcX + areaData['dRight'], centerBlockcY, areaData['rightInclineAngle'])
            dx = lineX - x
            dxCen = lineX - centerBlockcX
            dy = centerBlockcY - y
            dyCen = areaData['dTop']
            rateX = (dxCen - dx) / dxCen
            rateY = dy / dyCen
            resX = rateX * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resY = rateY * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0 # 做一个修正
        elif quadrant == 2:
            lineX = LineFromYGetX(y, centerBlockcX - areaData['dLeft'], centerBlockcY, areaData['leftInclineAngle'])
            dx = x - lineX
            dxCen = centerBlockcX - lineX
            dy = centerBlockcY - y
            dyCen = areaData['dTop']
            rateX = (dxCen - dx) / dxCen
            rateY = dy / dyCen
            resX = rateX * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resY = rateY * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0 # 做一个修正
            resX = resX * (-1)
        elif quadrant == 3:
            lineX = LineFromYGetX(y, centerBlockcX - areaData['dLeft'], centerBlockcY, areaData['leftInclineAngle'])
            dx = x - lineX
            dxCen = centerBlockcX - lineX
            dy = y - centerBlockcY
            dyCen = areaData['dBottom']
            rateX = (dxCen - dx) / dxCen
            rateY = dy / dyCen
            resX = rateX * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resY = rateY * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0 # 做一个修正
            resX = resX * (-1)
            resY = resY * (-1)
        elif quadrant == 4:
            lineX = LineFromYGetX(y, centerBlockcX + areaData['dRight'], centerBlockcY, areaData['rightInclineAngle'])
            dx = lineX - x
            dxCen = lineX - centerBlockcX
            dy = y - centerBlockcY
            dyCen = areaData['dBottom']
            rateX = (dxCen - dx) / dxCen
            rateY = dy / dyCen
            resX = rateX * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resY = rateY * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0 # 做一个修正
            resY = resY * (-1)
    else:
        dx = x - centerBlockcX
        dy = y - centerBlockcY
        dxCen = areaData['dRight'] if dx > 0 else areaData['dLeft']
        dyCen = areaData['dBottom'] if dy > 0 else areaData['dTop']
        udx = dx if dx > 0 else -dx
        udy = dy if dy > 0 else -dy
        if dx > 0:
            resX = udx / dxCen * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resY = 0
        elif dx < 0:
            resX = udx / dxCen * 20.5 - 0.5
            resX = int(resX) + 1 if resX > 0 else 0 # 做一个修正
            resX = - resX
            resY = 0
        elif dy > 0:
            resY = udy / dyCen * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0
            resY = - resY
            resX = 0
        elif dy < 0:
            resY = udy / dyCen * 20.5 - 0.5
            resY = int(resY) + 1 if resY > 0 else 0
            resX = 0
    return resX, resY


# 计算两点间的距离
def p2pDistance(p1, p2):
    p1x, p1y = p1
    p2x, p2y = p2
    return sqrt((p1x - p2x) ** 2 + (p1y - p2y) ** 2)


# 判断是否为符合要求的矩形
def isCorrectRectangle(points, span, wS, hS):
    p1, p2, p3, p4 = points
    flag = True
    w = p2pDistance(p1, p2)
    h = p2pDistance(p2, p3)
    if w > h:
        t = w
        w = h
        h = t
    s = w * h
    smn, smx = span
    flag = False if not (smn < s < smx) else True
    wmn, wmx = wS
    hmn, hmx = hS
    flag = False if not (wmn < w < wmx) else True
    flag = False if not (hmn < h < hmx) else True
    return flag


# 返回外接矩形框区域
def outLineRect(points):
    # p1, p2, p3, p4 = points
    xmn, xmx, ymn, ymx = 999, 0, 999, 0
    for p in enumerate(points):
        xmx = p[0] if p[0] > xmx else xmx
        xmn = p[0] if p[0] < xmn else xmn
        ymx = p[1] if p[1] > ymx else ymx
        ymn = p[1] if p[1] < ymn else ymn
    return xmn, ymn, xmx - xmn, ymx - ymn


# 求两点连线倾斜角的余弦值和正弦值
def p2pLineCosAndSin(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dis = p2pDistance(p1, p2)
    pl = p1 if x1 < x2 else p2
    pr = p2 if x1 < x2 else p1
    xl, yl = pl
    xr, yr = pr
    dx = xr - xl
    dCos = dx / dis
    dCos = dCos if yl > yr else -dCos
    dy = y2 - y1
    dy = dy if dy > 0 else -dy
    dSin = dy / dis
    return dCos, dSin


# 矩形微调
def RepairRect(points, wS, hS):
    l = []
    p1, p2, p3, p4 = points
    w = p2pDistance(p1, p2)
    h = p2pDistance(p2, p3)
    if w > h:
        t = w
        w = h
        h = t
    wmn, wmx = wS
    hmn, hmx = hS
    if wmn / w > w / wmx: # 外扩一些
        for i in range(4):
            l.append(BroadenPoint(i, points))
        return tuple(l)
    else:
        for i in range(4):
            l.append(ShrunkPoint(i, points))
        return tuple(l)


def BroadenPoint(idx, points):
    lidx, ridx = 0, 0
    if idx == 0:
        lidx = 3
        ridx = 1
    elif idx == 3:
        lidx = 2
        ridx = 0
    else:
        lidx = idx - 1
        ridx = idx + 1
    cos1, sin1 = p2pLineCosAndSin(points[lidx], points[idx])
    cos2, sin2 = p2pLineCosAndSin(points[idx], points[ridx])
    dis1 = p2pDistance(points[lidx], points[idx])
    dis2 = p2pDistance(points[idx], points[ridx])
    x, y = points[idx]
    if isUpLine(points[lidx], points[idx]):
        x = x + (dis1 / 16) * cos1
        y = y - (dis1 / 16) * sin1
    else:
        x = x - (dis1 / 16) * cos1
        y = y + (dis1 / 16) * sin1
    if isUpLine(points[idx], points[ridx]):
        x = x - (dis2 / 16) * cos2
        y = y + (dis2 / 16) * sin2
    else:
        x = x + (dis2 / 16) * cos2
        y = y - (dis2 / 16) * sin2
    t = tuple([x, y])
    return t


def ShrunkPoint(idx, points):
    lidx, ridx = 0, 0
    if idx == 0:
        lidx = 3
        ridx = 1
    elif idx == 3:
        lidx = 2
        ridx = 0
    else:
        lidx = idx - 1
        ridx = idx + 1
    cos1, sin1 = p2pLineCosAndSin(points[lidx], points[idx])
    cos2, sin2 = p2pLineCosAndSin(points[idx], points[ridx])
    dis1 = p2pDistance(points[lidx], points[idx])
    dis2 = p2pDistance(points[idx], points[ridx])
    x, y = points[idx]
    if isUpLine(points[lidx], points[idx]):
        x = x - (dis1 / 16) * cos1
        y = y + (dis1 / 16) * sin1
    else:
        x = x + (dis1 / 16) * cos1
        y = y - (dis1 / 16) * sin1
    if isUpLine(points[idx], points[ridx]):
        x = x + (dis2 / 16) * cos2
        y = y - (dis2 / 16) * sin2
    else:
        x = x - (dis2 / 16) * cos2
        y = y + (dis2 / 16) * sin2
    t = tuple([x, y])
    return t


def isUpLine(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (y2 < y1 and x2 > x1) or (y2 < y1 and x2 < x1)


# 上升线加上余弦值，减去正弦值，下降线减去余弦值，加上正弦值
# 分割直线
def splitLine2Points(p1, p2):
    n = 8 # 每条线分的段数
    resultList = [p1]
    dCos, dSin = p2pLineCosAndSin(p1, p2)
    x1, y1 = p1
    x2, y2 = p2
    UP = True if (y2 < y1 and x2 > x1) or (y2 < y1 and x2 < x1) else False
    dis = p2pDistance(p1, p2)
    span = dis / n
    for i in range(n):
        lastPoint = resultList[i]
        x, y = 0, 0
        if UP :
            if dCos > 0:
                x = lastPoint[0] + span * dCos
                y = lastPoint[1] - span * dSin
            else:
                x = lastPoint[0] + span * dCos
                y = lastPoint[1] - span * dSin
        else:
            if dCos > 0:
                x = lastPoint[0] - span * dCos
                y = lastPoint[1] + span * dSin
            else:
                x = lastPoint[0] - span * dCos
                y = lastPoint[1] + span * dSin
        t = tuple([x, y])
        resultList.append(t)
    resultList.append(p2)
    return resultList


# 第四题
def SendRectanglePoints(centerBlockcX, centerBlockcY, areaData):
    global sensor, img, canvaLMono, RectangleSize, RectWidthSize, RectHeightSize, MainRoiAreaL, uart, CenterBlockcX, CenterBlockcY, AreaData, led

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.set_brightness(1)

    loop = True
    rects = []
    while loop:
        img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
        img.midpoint(1, bias=0.5, threshold=True, offset=5, invert=True)
        img.dilate(1)
        rr = img.find_rects(roi=MainRoiAreaL)
#        img.draw_rectangle(MainRoiAreaL)
        if rr:
            for r in rr:
                if not isCorrectRectangle(r.corners(), RectangleSize, RectWidthSize, RectHeightSize):
                    pass
                    # print("不符合要求的矩形")
                else:
#                    img.draw_rectangle(r.rect(), color = (255, 0, 0))
                    for p in r.corners():
                        if not isInMainArea(p[0], p[1], centerBlockcX, centerBlockcY, areaData): # 去掉不在主区域内的
                            pass
                            # print("有点不在区域内")
                        else:
                            # print("满足的矩形坐标："+str(r.corners()))
                            rects.append(r.corners())
                            # print("len："+str(len(rects)))
                            if len(rects) == 50:
                                loop = False
    theMostFreqRect = tuple()
    theMostFreqRect = max(rects, key=rects.count)
    repairRect = RepairRect(theMostFreqRect, RectWidthSize, RectHeightSize)
#    print(repairRect)
    theResultPointsList = []
    p1, p2, p3, p4 = repairRect
    lis = []
    lis += splitLine2Points(p1, p2)
    lis += splitLine2Points(p2, p3)
    lis += splitLine2Points(p3, p4)
    lis += splitLine2Points(p4, p1)
    # 保证点的个数是4的整数
#    count = len(lis)
#    bal = count % 4
#    for i in range(4 - bal):
#        lis.append(lis[0])
    lis.append(lis[0])
    lis_ = []
    for p in lis:
        x, y = p
        x = x * 4
        y = y * 4
        t = tuple([x, y])
        lis_.append(t)

    lis_.reverse()
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.VGA)
    sensor.set_brightness(1)
#    while 1:
#        img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
#        for p in lis_:
#            x, y = int(p[0]), int(p[1])
#            img.draw_circle(x, y, 5, color = (0, 255, 0))
#    print(lis_)
#    return lis_
    mapPoints = []
    for p in lis_:
        #
#        img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
#        img.draw_circle(int(p[0]), int(p[1]), 5, color = (0, 255, 0))
#        time.sleep(0.4)
        #
        x, y = GetBlockXYinMap(p[0], p[1], CenterBlockcX, CenterBlockcY, AreaData)
        t = tuple([x, y])
        mapPoints.append(t)


    for p in mapPoints:
        resStr = FormatPoint(p)
        led.on()
        Send_Message(resStr)
        led.off()
#        print(resStr)
        while uart.read() != '!':
            pass
#        time.sleep(0.4)

#def SendData(points, centerBlockcX, centerBlockcY, areaData):
#    mapPoints = []
#    for p in enumerate(points):
#        xx, yy = p
#        x, y = GetBlockXYinMap(xx, yy, centerBlockcX, centerBlockcY, areaData)
#        t = tuple([x, y])
#        mapPoints.append(t)


#    for p in mapPoints:
#        resStr = FormatPoint(p)
#        Send_Message(resStr)
#        print(resStr)
#        time.sleep(0.2)



# 初始化部分
# 当前只有一个校准点的写法
# 得到坐标原点方块左上角坐标
CenterBlockcX, CenterBlockcY = SetTheMapSourcePoint()
# CenterBlockcX, CenterBlockcY = 345, 220
CenterBlockcXL, CenterBlockcYL = CenterBlockcX * 0.25, CenterBlockcY * 0.25
# CenterBlockcXL, CenterBlockcYL = 76, 75

# 重新框出主要区域
MapPoints = BuildCoordinate(CenterBlockcX, CenterBlockcY, AreaData)
MapPointsL = BuildCoordinate(CenterBlockcXL, CenterBlockcYL, AreaDataL)

MainRoiArea = (MapPoints['BottomLeft'][0],
              MapPoints['BottomLeft'][1] - AreaData['dBottom'] - AreaData['dTop'],
              MapPoints['BottomRight'][0] - MapPoints['BottomLeft'][0],
              AreaData['dBottom'] + AreaData['dTop'])
MainRoiAreaL = (MapPointsL['BottomLeft'][0],
              MapPointsL['BottomLeft'][1] - AreaDataL['dBottom'] - AreaDataL['dTop'],
              MapPointsL['BottomRight'][0] - MapPointsL['BottomLeft'][0],
              AreaDataL['dBottom'] + AreaDataL['dTop'])


led = LED(3)
led.on()
#SendRectanglePoints(CenterBlockcXL, CenterBlockcYL, AreaDataL)
#SendData(points, CenterBlockcX, CenterBlockcY, AreaData)

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)

    DrawMap(CenterBlockcX, CenterBlockcY, MapPoints)
#    if uart.any():
#        print("接收到了")
    response = uart.read()
    if response:
#        print("接收")
        if response == '!':
#            print("验证")
            led.off()
#            Send_Message("-10+10+10+10+10-10-10-10\r")
#            break
            SendRectanglePoints(CenterBlockcXL, CenterBlockcYL, AreaDataL)
            break

#    Send_Message("-10+10+10+10+10-10-10-10\r")

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.VGA)    # Set frame size to QVGA (320x240)

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)
    DrawMap(CenterBlockcX, CenterBlockcY, MapPoints)
