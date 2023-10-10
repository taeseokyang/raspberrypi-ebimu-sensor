import serial
import datetime

nowTime = str(datetime.datetime.now())
fileName = nowTime[:10]+"_"+nowTime[11:21]

try:
    f = open(fileName, 'w')
except:
    print("Failed to open file")

#ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001) #when connect to usb
ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001) #when connect to pins (tx4,rx5)
buf = ""

while True:
    # read value
    while ser.inWaiting():
        data = str(ser.read()).strip()
        buf += data # buffering
        if data[3] == "n": # last data of one line is '\n' so when data[3] is n then do decode 
            buf = buf.replace("'","") # remove (') and (b) because data has (') and (b) like this b'10.55' 
            buf = buf.replace("b","") 
            
            # split each data
            try :roll, pitch, yaw = map(float,buf[1:-4].split(','))
            except:
                print("Invalid Data")
                continue
            
            try :f.write(data)
            except :
                print("File write failed")
                continue

            print(roll,pitch,yaw)
            buf = ""

# f.close()