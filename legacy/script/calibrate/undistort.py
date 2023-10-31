import cv2
import sys
import numpy as np

def undistort(img_path):
    DIM = (640, 480)
    K = np.array(
        [[529.0542108650583, 0.0, 328.11243708259155], [0.0, 528.4474102469408, 276.541015762088], [0.0, 0.0, 1.0]])
    D = np.array([[-0.1675384798926949], [-0.5110533326571545], [10.49841774261518], [-41.314556160738114]])
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # for p in sys.argv[1:]:
    #     print(p)
    undistort("7.jpg")
