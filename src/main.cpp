#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/opencv.hpp>
#include <stdio.h>

using namespace cv;

int main(int argc, char **argv) {
  Mat mat;
  VideoCapture cap(0);
  cap.set(CAP_PROP_FRAME_WIDTH, 1080); // 宽度
  cap.set(CAP_PROP_FRAME_HEIGHT, 960); // 高度
  cap.set(CAP_PROP_FPS, 30);           // 帧数
  cap.set(CAP_PROP_BRIGHTNESS, 1);     // 亮度 1
  cap.set(CAP_PROP_CONTRAST, 40);      // 对比度 40
  cap.set(CAP_PROP_SATURATION, 50);    // 饱和度 50
  cap.set(CAP_PROP_HUE, 50);           // 色调 50
  cap.set(CAP_PROP_EXPOSURE, 50);      // 曝光 50

  while (true) {
    cap >> mat;
    if (!mat.empty()) {
      imshow("aaa", mat);
      waitKey(1);
    }
  }
  return 0;
}
