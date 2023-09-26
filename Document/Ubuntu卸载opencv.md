# Ubuntu卸载opencv方法

## 第一步 找到opencv安装目录，进入build文件，终端输入：
~~~
sudo make uninstall
cd ..
sudo rm -r build
sudo rm -r /usr/local/include/opencv2 /usr/local/include/opencv /usr/include/opencv /usr/include/opencv2 /usr/local/share/opencv /usr/local/share/OpenCV /usr/share/opencv /usr/share/OpenCV /usr/local/bin/opencv* /usr/local/lib/libopencv*
~~~
然后直接把opencv文件夹删除

## 第二步 卸载 /usr中的opencv相关内容，终端输入：

>cd /usr/
>
>find . -name "*opencv*" | xargs sudo rm -rf

## 第三步 移除其他opencv相关内容
>chmod a+x /home/***/opencv
>
>rm -r /home/***/opencv

## 第四步 移除python相关项
>sudo apt-get remove opencv-doc opencv-data python-opencv

## 检查是否留存
>pkg-config opencv --libs
>
>pkg-config opencv --modversion