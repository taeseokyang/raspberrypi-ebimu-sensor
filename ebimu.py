import time
import serial

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
            print(roll,pitch,yaw)
            buf = " "
    time.sleep(0.05)
