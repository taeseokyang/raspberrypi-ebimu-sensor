import time
import serial
from matplotlib import pyplot as plt
import numpy as np

max_points = 100
fig = plt.figure()
plt.subplots_adjust(left=0.125, bottom-0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.5)
accelAxes = fig.add_subplot(1,1,1,xlim(0, max_points), ylim=(-3.0,3.0))

accelAxes.set_title("test")
accelLineX, = accelAxes.plot([],[], lw=2)
accelLineX, = accelAxes.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='x')

accelXBunch = []




def init():
    return accelLineX

def aniate(i):
    

def serialSensorRead():
    while ser.inWating():
        data = str(ser.read()).strip()
        buf += data
        

#ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001)#usb
ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001)#tx4,rx5
buf = ""
while True:
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data
        if data[3] == "n":
            buf = buf.replace("'","")
            buf = buf.replace("b","")
            roll, pitch, yaw = map(float,buf[2:-4].split(','))
            accelXBunch.append(roll)
            print(roll,pitch,yaw)
            buf = " "
    time.sleep(0.05)
    plt.show()
