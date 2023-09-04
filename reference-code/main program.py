import time
import RPi.GPIO as GPIO
import serial 
import picamera
import cv2
import cv2 as cv
import numpy as np
from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar
from PCAPWM import *
from chassis import *
from arm import *
from vision import *
global x
global y
global p
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)
jd=[150,150,150,150,150,150,150,150,150,150,150,150,150,150,150]
bh=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
def xj():
            step1()
            smdw()
            step2()
            tz(0)
            yssb(1)
            step3(1)
            step4(1)
            step5()
            tz(0)
            yssb(2)
            step3(2)
            step4(2)
            step6()
            
def home():
        start()
        zp(5)
        setup()
        gd()
        setupbjdj()
        fwbj()
        move1(5,5,5000)
        time.sleep(0.5)     
if __name__ == '__main__':
    try:
        print('home')
        home()
        p=0
        while p<1:
            if GPIO.input(35) == 0:
                p+=1
        p=0
  
        while 1:
            xj()
            

            break
    except KeyboardInterrupt:
        print('over')
        move(0,0,0)