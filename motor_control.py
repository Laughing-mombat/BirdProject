import RPi.GPIO as GPIO
import time

def main(Rot_deg, Rot_Dir, motor):
    delay = 0.001

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    ControlPin0 = [7,11,13,15]
    ControlPin1 = [8,10,12,16]

    for pin in ControlPin0, ControlPin1:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin,0)

    seq = [[1,0,0,1],
           [1,0,0,0],
           [1,1,0,0],
           [0,1,0,0],
           [0,1,1,0],
           [0,0,1,0],
           [0,0,1,1],
           [0,0,0,1]]

    Rot_steps = int((Rot_deg/360)*4096)
    halfstep = 0
    for i in range(Rot_steps):    
        if motor == 0:
            for pin in range(4):
                GPIO.output(ControlPin0[pin], seq[halfstep][pin])
        elif motor == 1:
            for pin in range(4):
                GPIO.output(ControlPin1[pin], seq[halfstep][pin])
        elif motor == 2:
            for pin in range(4):
                GPIO.output(ControlPin0[pin], seq[halfstep][pin])
            for pin in range(4):
                GPIO.output(ControlPin1[pin], seq[halfstep][pin])
        halfstep += Rot_Dir
        if (halfstep >= 8):
            halfstep = 0
        elif halfstep < 0:
            halfstep = 7
        time.sleep(delay)
    GPIO.cleanup()
    

if __name__ == "__main__":
    main(Rot_deg, Rot_Dir, motor)
