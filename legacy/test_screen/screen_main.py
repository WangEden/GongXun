import time
# import datatime
import os
import sys
import traceback
import threading
import subprocess


if __name__ == "__main__":
    loader = subprocess.Popen(["/usr/bin/python3", "/home/pi/GongXun/test_screen/test_screen.py"])

    k = 0
    while k < 10:
        print("k: ", k)
        time.sleep(0.5)
        k+=1
    
    
