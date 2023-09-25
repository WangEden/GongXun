使用终端
使用nano打开文件
sudo nano /etc/gdm3/custom.conf

在文件的[daemon]部分中添加以下两行代码：
#usename值为自己的登录用户名
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=username

保存并关闭，注意usename值的是你自己登录的用户名

第二步
sudo nano /etc/pam.d/gdm-password

注释掉下面一行

auth    required    pam_succeed_if.so user != root quiet_success

保存并关闭文件，重启计算机。