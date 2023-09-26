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
accelLineX, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='x')
plt.ylim(-100,100)
plt.xlim(0,100)
accelLineY, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='y')
accelLineZ, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='z')

def init():
    return accelLineX, accelLineY, accelLineZ

def animate(i):
    accelX, accelY, accelZ = getAllSensorDataOnQueue()

    if (accelX.count == 0 or accelY.count == 0 or accelZ.count == 0):
        return
    # accel
    oldAccelX = accelLineX.get_ydata()
    newAccelX = np.r_[oldAccelX[1:], accelX]
    newAccelX = newAccelX[-100:]
    accelLineX.set_ydata(newAccelX)

    #oldAccelY = accelLineY.get_ydata()
    #newAccelY = np.r_[oldAccelY[1:], accelY]
    #accelLineY.set_ydata(newAccelY[-100:])

    #oldAccelZ = accelLineZ.get_ydata()
    #newAccelZ = np.r_[oldAccelZ[1:], accelZ]
    #accelLineZ.set_ydata(newAccelZ[-100:])
    return accelLineX, accelLineY, accelLineZ
    

sensorDataQueue = queue.Queue()
def serialSensorRead(i):
    buf = " "
    while 1:
        while ser.inWaiting():
            data = str(ser.read()).strip()
            buf += data
            if data[3] == "n":
                buf = buf.replace("'","")
                buf = buf.replace("b","")
                roll, pitch, yaw = map(float,buf[2:-4].split(','))
                sensorDataQueue.put((roll,pitch,yaw))
                print(roll,pitch,yaw)
                buf = " "
        time.sleep(0.05)

def getAllSensorDataOnQueue():
    accelXBunch = []
    accelYBunch = []
    accelZBunch = []
    while not sensorDataQueue.empty():
        accelX, accelY, accelZ= sensorDataQueue.get_nowait()
        accelXBunch.append(accelX)
        accelYBunch.append(accelY)
        accelZBunch.append(accelZ)
    return tuple(accelXBunch), tuple(accelYBunch), tuple(accelZBunch)

        
#serialSensorReadThread = threading.Thread(target=serialSensorRead, args=(1,), daemon=True)
#serialSensorReadThread.start()

serialSensorRead(1)
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)

plt.show()

os.system("pause")
 
