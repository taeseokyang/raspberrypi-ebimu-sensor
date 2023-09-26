import time
import serial
import os
import threading
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import queue

#ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001)#usb
ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001)#tx4,rx5

max_points = 100

fig=plt.figure()
accelLineX, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='red', label='x')
accelLineY, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='green', label='y')
accelLineZ, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='blue', label='z')
plt.ylim(-100,100)
plt.xlim(0,100)

def init():
    return accelLineX, accelLineY, accelLineZ

def animate(i):
    rolls = []
    roll, pitch, yaw = '0','0','0'
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data
        if data[3] == "n":
            buf = buf.replace("'","")
            buf = buf.replace("b","")
            roll, pitch, yaw = map(float,buf[2:-4].split(','))
            rolls.append(roll)
            print(roll,pitch,yaw)
            buf = " "

    # accel
    oldAccelX = accelLineX.get_ydata()
    newAccelX = np.r_[oldAccelX[1:], rolls]
    newAccelX = newAccelX[-100:]
    accelLineX.set_ydata(newAccelX)

    #oldAccelY = accelLineY.get_ydata()
    #newAccelY = np.r_[oldAccelY[1:], accelY]
    #accelLineY.set_ydata(newAccelY[-100:])

    #oldAccelZ = accelLineZ.get_ydata()
    #newAccelZ = np.r_[oldAccelZ[1:], accelZ]
    #accelLineZ.set_ydata(newAccelZ[-100:])
    return accelLineX, accelLineY, accelLineZ
        
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)

plt.show()

os.system("pause")
