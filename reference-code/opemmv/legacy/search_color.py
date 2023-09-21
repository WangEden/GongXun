# LOTS OF Blob Detection
import sensor, image, time
from pyb import UART
from pyb import LED

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位、


# 参考右侧的LAB Color Space里面的参数
# （minL, maxL, minA, maxA, minB, maxB）
# 灰度图的阈值格式
# (min, max)

# 红色阈值
red_threshold =(42, 0, 10, 127, 15, 96)
# 黄色阈值
yellow_threshold = (45, 97, -27, 36, 30, 78)

green_threshold =(82, 33, -73, -24, -41, 62)


# 颜色1: 红色的颜色代码
red_color_code = 1 # code = 2^0 = 1
# 颜色2: 绿色的颜色代码
yellow_color_code = 2 # code = 2^1 = 2
# 颜色3: 绿的代码
green_color_code = 4# code = 2^2 = 4


sensor.reset() # 初始化摄像头
sensor.set_pixformat(sensor.RGB565) # 选择像素模式 RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) #关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。

clock = time.clock() # Tracks FPS.

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # 拍照，返回图像
    # 在图像中寻找满足颜色阈值约束(color_threshold, 数组格式), 像素阈值pixel_threshold， 色块面积大小阈值(area_threshold)的色块
    blobs = img.find_blobs([red_threshold, yellow_threshold ,green_threshold],  pixels_threshold=100, area_threshold=100)
    if blobs:
    #如果找到了目标颜色
        for blob in blobs:
        #迭代找到的目标颜色区域
            x = blob[0]
            y = blob[1]
            width = blob[2] # 色块矩形的宽度
            height = blob[3] # 色块矩形的高度
            center_x = blob[5] # 色块中心点x值
            center_y = blob[6] # 色块中心点y值
            color_code = blob[8] # 颜色代码

            # 添加颜色说明
            if color_code == red_color_code:
                img.draw_string(x, y - 10, "red", color = (0xFF, 0x00, 0x00))
                uart.write('r')
                uart.write('!')
            elif color_code == yellow_color_code:
                img.draw_string(x, y - 10, "yellow", color = (0xFF, 0x00, 0x00))
                uart.write('y')
                uart.write('!')
            elif color_code == green_color_code:
                img.draw_string(x, y - 10, "green", color = (0xFF, 0x00, 0x00))
                uart.write('g')
                uart.write('!')

        #用矩形标记出目标颜色区域
        img.draw_rectangle([x, y, width, height])
        #在目标颜色区域的中心画十字形标记
        img.draw_cross(center_x, center_y)

    print(clock.fps())
    time.sleep_ms(30)
