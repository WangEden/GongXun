#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/core.hpp>
using namespace cv;
using namespace std; 

int main(int argc, const char * argv[]) 
{
    cout<<"version"<<endl;
    cout<<CV_VERSION<<endl;
    // // vector<VideoCapture> devices;
    // String cameraPath = "/dev/video3";
    // VideoCapture cap(0);
    // cout << "argv: " << argv[2] << endl;
    // if (cap.isOpened()) 
    // {
    //     cout << "图像宽度：" << cap.get(CAP_PROP_FRAME_WIDTH) << endl; 
    //     cout << "图像高度：" << cap.get(CAP_PROP_FRAME_HEIGHT) << endl; 
    //     cout << "视频帧率：" << cap.get(CAP_PROP_FPS) << endl;
    // }
    // else
    // {
    //     cout << "无法打开摄像头" << endl;
    //     return -1;
    // }

    // while (true) 
    // {
    //     Mat frame;
    //     cap >> frame;
    //     if (frame.empty())
    //         break;
    //     imshow("camera0", frame);
    //     if (waitKey(1000 / cap.get(CAP_PROP_FPS)) == 32)
    //         break;
    // }
    return 0;
}