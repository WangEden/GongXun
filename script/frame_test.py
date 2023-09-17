import cv2 
import numpy as np
import Functions as F

cap = cv2.VideoCapture("/dev/video0")
#ret,frame = cap.read()
ret = cap.isOpened()
fps = cap.get(5)/10000  #查询帧率



while ret:
    ret,frame = cap.read()
    tstep = cap.get(1)
    circles = F.get_circle_center(frame)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype('int')
        for (x, y, r) in circles:
            cv2.circle(img_note, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(img_note, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    cv2.imshow("frame",frame)
    iloop=fps/2  #每秒处理2帧
    print("fps"+str(fps))

    while iloop:
        cap.grab()  #只取帧不解码，
        iloop =iloop - 1
        if iloop <1 :
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        break
cv2.destroyAllWindows()
cap.release()
