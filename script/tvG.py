import cv2

cap = cv2.VideoCapture(0)  # 打开摄像头

'''
while (1):
    # get a frame
    ret, frame = cap.read()
    #frame = cv2.flip(frame, 1)  # 摄像头是和人对立的，将图像左右调换回来正常显示
    # show a frame
    cv2.imshow("capture", frame)  # 生成摄像头窗口

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 如果按下q 就截图保存并退出
        cv2.imwrite("test.png", frame)  # 保存路径
        break
'''
n = 0
with open( "T.txt", "r") as file:
    s = file.read()
    n = int(s)
    print(s)

t = n

while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame) # 生成摄像头窗口

    if cv2.waitKey(10) & 0xFF == ord("q"):
        cv2.imwrite(f".~/GongXun/script/biaoding/a+{n}.jpg", frame) # 保存路径
        print(f"take {n} photo")
        n = 0

with open( "T.txt", "w") as file:
    file.write(str(t+1))

cap.release()
cv2.destroyAllWindows()
