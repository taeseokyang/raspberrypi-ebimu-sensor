import time
import serial

import threading
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import queue

#ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001)#usb
ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001)#tx4,rx5
buf = ""

max_points = 100
fig = plt.figure()
plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.5)
accelAxes = fig.add_subplot(1,1,1, xlim=(0, max_points), ylim=(-3.0,3.0))

accelAxes.set_title("test")
accelLineX, = accelAxes.plot([],[], lw=2)
accelLineX, = accelAxes.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='x')
accelLineY, = accelAxes.plot([],[], lw=2)
accelLineY, = accelAxes.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='y')
accelLineZ, = accelAxes.plot([],[], lw=2)
accelLineZ, = accelAxes.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=2, color='red', label='z')

def init():
    return accelLineX, accelLineY, accelLineZ

def animate():
    accelX, accelY, accelZ = getAllSensorDataOnQueue()
    # 예외 처리
    if (accelX.count == 0 or accelY.count == 0 or accelZ.count == 0):
        return
    # accel
    oldAccelX = accelLineX.get_ydata()
    newAccelX = np.r_[oldAccelX[1:], accelX]
    accelLineX.set_ydata(newAccelX)

    oldAccelY = accelLineY.get_ydata()
    newAccelY = np.r_[oldAccelY[1:], accelY]
    accelLineY.set_ydata(newAccelY)

    oldAccelZ = accelLineZ.get_ydata()
    newAccelZ = np.r_[oldAccelZ[1:], accelZ]
    accelLineZ.set_ydata(newAccelZ)
    return accelLineX, accelLineY, accelLineZ
    

sensorDataQueue = queue.Queue()
def serialSensorRead():
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data
        if data[3] == "n":
            buf = buf.replace("'","")
            buf = buf.replace("b","")
            roll, pitch, yaw = map(float,buf[2:-4].split(','))
            sensorDataQueue.put((roll,pitch,yaw))
            #print(roll,pitch,yaw)
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

        
serialSensorReadThread = threading.Thread(target=serialSensorRead, daemon=True)
serialSensorReadThread.start()

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)
plt.show()
 
