import RPi.GPIO as GPIO
import time
TERMINAL1 = 37 
TERMINAL2 = 38 
def setupbjdj():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TERMINAL1, 0)
    GPIO.setup(TERMINAL2, 0)
    GPIO.setup(35, GPIO.IN)
   

def startbj(pulse_terminal):
    pulse_terminal.start(0)
    pulse_terminal.ChangeDutyCycle(50) 

def down(a):
    pulse_terminal = GPIO.PWM(TERMINAL1, a) 
    set_direction(1)
    startbj(pulse_terminal)
    time.sleep(2)
def down1(a):
    pulse_terminal = GPIO.PWM(TERMINAL1, a) 
    set_direction(1)
    startbj(pulse_terminal)
    time.sleep(0.7)
def up(a):
    pulse_terminal = GPIO.PWM(TERMINAL1, a) 
    set_direction(0)
    startbj(pulse_terminal)
    time.sleep(2)
def up1(a):
    pulse_terminal = GPIO.PWM(TERMINAL1, a) 
    set_direction(0)
    startbj(pulse_terminal)
    time.sleep(0.1)
 
def set_direction(direction=0):
    GPIO.output(TERMINAL2, direction) 

def fwbj():
    i=0
    while i < 1:
        up1(5000)
        if GPIO.input(35) == 0:
            print('0')
            time.sleep(0.2)
            if GPIO.input(35) == 0:
                time.sleep(0.5)
                print(1)
                i+=1
            else:
                fwbj()
    down(320)
    print('finish')

if __name__ == '__main__':# Program start from here
    try:
        setupbjdj()
        while 1:
#             down(4000)
#             down(8000)
#             move(1)
#             up(20000)
#             i=0
#             while i < 10:
#             print(GPIO.input(35))
#             time.sleep(0.5)
#                 i+=1
#             fwbj()
            print('1')
#             GPIO.cleanup()
            break
    except KeyboardInterrupt:
            GPIO.cleanup()
