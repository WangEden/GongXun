
import sensor, image, time, ustruct, math
from pyb import UART

black_threshold = (5, 32, -21, 11, -14, 24)  # 黑色阈值
gray_thresholds = (0, 100, 7, 127, -128, 127)  # 还没改成铅笔灰
light_thresholds = (99, 100, -128, 127, -128, 127) # 激光中心阈值

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # grayscale is faster (160x120 max on OpenMV-M7)
sensor.set_framesize(sensor.HQVGA)  # 1m距离刚好
sensor.skip_frames(time=2000)
clock = time.clock()

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)


def find_max(rects):  # 定义函数选取元素面积最大
    max_size = 0  # 初值为0
    for rect in rects:  # for循环迭代
        if rect.w() * rect.h() > max_size:  # 被测物体面积 = blob[2]*blob[3]
            max_rect = rect
            max_size = rect.w() * rect.h()
    return max_rect


def send_data_packet(a, b, c, d, i, f, g, h):
    temp = ustruct.pack("<bhhhhhhhhb",  # 格式为俩个字符俩个整型
                        0x2C,  # 帧头1
                        int(a),  # up sample by 2    #数据1
                        int(b),  # up sample by 2    #数据2
                        int(c),
                        int(d),
                        int(i),
                        int(f),
                        int(g),
                        int(h),
                        0x5B)  # 针尾
    for x in range(5):
        uart.write(temp);  # 串口发送
        time.sleep_ms(100)



while (True):
    clock.tick()
    img = sensor.snapshot()
    rects1 = img.find_rects(roi = [65,10,190,120],threshold=15500)#防误识别
    if rects1:
        max_rect1 = find_max(rects1)
        img.draw_rectangle(max_rect1.rect(), color=(255, 0, 0))
        for p in max_rect1.corners(): img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))

    img = sensor.snapshot()
    rects2 = img.find_rects(roi = [65,10,190,120],threshold=15500)
    if rects2 and rects1:
        max_rect2 = find_max(rects2)
        img.draw_rectangle(max_rect2.rect(), color=(255, 0, 0))
        for p in max_rect2.corners(): img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))
    #判断是否为同一目标
        if abs(max_rect1.corners()[0][0]-max_rect2.corners()[0][0]) < 5 and abs(max_rect1.corners()[0][1]-max_rect2.corners()[0][1])<5:
            send_data_packet(max_rect2.corners()[0][0]-1, max_rect2.corners()[0][1]-1,
                             max_rect2.corners()[1][0]-1, max_rect2.corners()[1][1]+1,
                             max_rect2.corners()[2][0]+1, max_rect2.corners()[2][1]+1,
                             max_rect2.corners()[3][0]+1, max_rect2.corners()[3][1]-1)

            print(max_rect2.corners())



    print("FPS %f" % clock.fps())

