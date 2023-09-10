from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2

save_path = '../static/imgs/qrcode_result/'
camera_path = '/dev/camera0'

cap = cv2.VideoCapture(camera_path)
cap.set(3, 640)
cap.set(4, 480)
cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

try:
    ret, frame = cap.read()
    img_gray = None
    if ret:
        img_gray = frame.copy()
        img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)

    while True:
        

except:

# def detect_qrcode():
#     global tt
#     tt=[]
#     tp = "1.jpg"
#     img = cv2.imread(tp) 
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     result = pyzbar.decode(gray)
#     if result == []: 
#         print("二维码识别失败")
#     else:
#         for i in result:
#             tt=i.data.decode("utf-8")
#         print('二维码识别成功')
#         print(tt)
#         width = 400
#         height = 400
#         img = np.ones((height, width, 4)) * (255, 255, 255, 0)
#         text = tt
#         cv2.putText(img, text, (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 10)
#         cv.imwrite("image.jpg", img);
#         img=Image.open('image.jpg')
#         img.show()
#         num = ''.join([x for x in tt if x.isdigit()])
#         print(num)
#         for i in range (0, 6) :
#             z[5-i] = int (num) // (10 ** i) % 10            
#         print(z)
#         return tt