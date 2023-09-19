#include <iostream>
#include <opencv2/highgui.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/videoio.hpp>

using namespace std;
using namespace cv;

int main(int, char**){
    VideoCapture capture(0);
    Mat mat;
    while(true)
    {
        capture.read(mat);
        imshow("image", mat);
        cout << "Hello, from app!\n";
    }
}
