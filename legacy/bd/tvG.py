import cv2

cap = cv2.VideoCapture(0)  # 打开摄像头

n = 0
with open( "T.txt", "r") as file:
    s = file.read()
    n = int(s)
    print(s)

while n > 0:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("q capture", frame) # 生成摄像头窗口

    if cv2.waitKey(10) & 0xFF == ord("t"):
        cv2.imwrite(f"./20mma{n}.jpg", frame) # 保存路径
        print(f"take {n} photo")
        n+=1

    if cv2.waitKey(10) & 0xFF == ord("q"):
    	break

t = n

with open( "T.txt", "w") as file:
    file.write(str(t+1))

cap.release()
cv2.destroyAllWindows()
