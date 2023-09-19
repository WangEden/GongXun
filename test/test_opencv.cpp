#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc/imgproc.hpp>
using namespace cv;
 
int main(int argc, const char * argv[]) {
    Mat image;
    VideoCapture capture(0);//打开摄像头
    while(1){
    	capture>>image;
	    imshow("test",image);
	    waitKey(20);
    }
}