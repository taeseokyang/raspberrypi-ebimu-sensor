import time
import serial
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np

#ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001) #when connect to usb
ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001) #when connect to pins (tx4,rx5)

# maek graph 
max_points = 100
fig=plt.figure()
accelLineX, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='red', label='roll')
accelLineY, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='green', label='pitch')
accelLineZ, = plt.plot(np.arange(max_points), np.ones(max_points, dtype=np.float64)*np.nan, lw=1, color='blue', label='yaw')
plt.ylim(-200,200)
plt.xlim(0,100)
plt.title('Ebimu Live Plotter')
plt.legend()

# init function for animation function
def init():
    return accelLineX, accelLineY, accelLineZ

# animate function for animation function
def animate(_):
    buf = ""
    # read value
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data # buffering
        if data[3] == "n": # last data of one line is '\n' so when data[3] is n then do decode 
            buf = buf.replace("'","") # remove (') and (b) because data has (') and (b) like this b'10.55' 
            buf = buf.replace("b","") 
           
            # split each data
            try :
                roll, pitch, yaw = map(float,buf[1:-4].split(','))
            except:
                continue

            print(roll,pitch,yaw)
            buf = ""

            # graph update
            oldAccelX = accelLineX.get_ydata()
            newAccelX = np.r_[oldAccelX[1:], roll]
            accelLineX.set_ydata(newAccelX[-100:])

            oldAccelY = accelLineY.get_ydata()
            newAccelY = np.r_[oldAccelY[1:], pitch]
            accelLineY.set_ydata(newAccelY[-100:])

            oldAccelZ = accelLineZ.get_ydata()
            newAccelZ = np.r_[oldAccelZ[1:], yaw]
            accelLineZ.set_ydata(newAccelZ[-100:])
    
    return accelLineX, accelLineY, accelLineZ

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)
plt.show()
