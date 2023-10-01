import cv2
 
<<<<<<< HEAD
cap = cv2.VideoCapture("/dev/cameraTop")
=======
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("/dev/video0")
>>>>>>> 2d7c27c4b7f3e749f4f01b9704e0c4a2517ae343
cap.set(3, 640)
cap.set(4, 480)
cap.set(cv2.CAP_PROP_AUTO_WB,1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,1)
cap.set(cv2.CAP_PROP_EXPOSURE,7)
cap.set(6, cv2.VideoWriter.fourcc(*'MJPG'))

# 设置编码类型为mp4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# 得到摄像头拍摄的视频的宽和高
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# 创建对象，用于视频的写出
n = 0
with open( "video.txt", "r") as file:
    s = file.read()
    n = int(s)
    print(s)

t = n
path = './video'+str(n)+'.mp4'
videoWrite = cv2.VideoWriter(path, fourcc, 25, (width,height))
 
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # 将图片写入视频
    videoWrite.write(frame)
    cv2.imshow('frame', frame)
 
    if cv2.waitKey(33) & 0xFF == ord('q'):
        break
# 刷新，释放资源
videoWrite.release()
cap.release()
cv2.destroyAllWindows()

with open( "video.txt", "w") as file:
    file.write(str(t+1))
