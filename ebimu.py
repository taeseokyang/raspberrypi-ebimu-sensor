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
plt.ylim(-200,200)
plt.xlim(0,100)

def init():
    return accelLineX, accelLineY, accelLineZ

def animate(i):
    rolls = []
    pitches = []
    yaws = []
    buf = ""
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data
        if data[3] == "n":
            buf = buf.replace("'","")
            buf = buf.replace("b","")
            #if it is not num then error
            roll, pitch, yaw = map(float,buf[2:-4].split(','))
            print(roll,pitch,yaw)
            rolls.append(roll)
            pitches.append(pitch)
            yaws.append(yaw)
            buf = " "
    #print(rolls)



    oldAccelX = accelLineX.get_ydata()
    newAccelX = np.r_[oldAccelX[1:], rolls[1:]]
    accelLineX.set_ydata(newAccelX[-100:])

    oldAccelY = accelLineY.get_ydata()
    newAccelY = np.r_[oldAccelY[1:], pitches[1:]]
    accelLineY.set_ydata(newAccelY[-100:])

    oldAccelZ = accelLineZ.get_ydata()
    newAccelZ = np.r_[oldAccelZ[1:], yaws[1:]]
    accelLineZ.set_ydata(newAccelZ[-100:])
    return accelLineX, accelLineY, accelLineZ
        
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)

plt.show()

os.system("pause")
