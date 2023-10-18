import time
import board
import busio
import digitalio
import adafruit_bmp280
import RPi.GPIO as GPIO
import numpy as np

import serial # for ebimu
import datetime # for ebimu

import multiprocessing # for multiprocessing

def ebimu_process(n):
    # make file and open
    nowTime = str(datetime.datetime.now())
    fileName = nowTime[:10]+"_"+nowTime[11:21]
    try:
        f = open(fileName, 'w')
        log = open("log.txt",'w')
    except:
        print("Failed to open file")

    # connect ebimu
    #ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001) #when connect to usb
    ser = serial.Serial('/dev/ttyAMA1',115200,timeout=0.001) #when connect to pins (tx4,rx5)
    buf = "" # for ebimu
    while True:
        # read ebimu value 
        while ser.inWaiting():
            data = str(ser.read()).strip()
            buf += data # buffering
            if data[3] == "n": # last data of one line is '\n' so when data[3] is n then do decode 
                buf = buf.replace("'","") # remove (') and (b) because data has (') and (b) like this b'10.55' 
                buf = buf.replace("b","") 
                
                # split each data
                try :
                    roll, pitch, yaw, x, y, z = map(float,buf[1:-4].split(','))
                except Exception as e:
                    print("Error from data processing : ", e)
                    log.write(str(e)+"\n")
                    buf = ""
                    continue
                
                try :
                    datas = [roll,pitch,yaw,x,y,z]
                    writeString = "*"+str(datas)[1:-1]+"\n"
                    f.write(writeString)
                except Exception as e:
                    print("Error from file writing : ", e)
                    log.write(str(e)+"\n") # it also can make error but .. maybe.. i dont think so
                    continue

                print(roll,pitch,yaw,x,y,z)
                buf = ""

if __name__ == '__main__':
    eb_p = multiprocessing.Process(target=ebimu_process, args=(1,))
    eb_p.start()

    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.D6)
    bmp280 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)
    bmp280.sea_level_pressure = 1013.25

    GPIO.setmode(GPIO.BCM)
    servo_pin = 18
    GPIO.setwarnings(False)
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)

    def moving_average(data, window):
        moving_avg = []
        for i in range(len(data)):
            if i < window:
                moving_avg.append(data[i])
            else:
                partial_avg = np.mean(data[i - window + 1 : i + 1])
                moving_avg.append(partial_avg)
        return moving_avg

    window = 3
    data = []
    moving_std = []
    alpha = 0.25
    beta = 0.125
    temp_altitude = []
    init_altitude = 0  

    while True:
        altitude = bmp280.altitude
        if init_altitude == 0:
            init_altitude = altitude
        
        cali_altitude = altitude - init_altitude
        result = cali_altitude
        data.append(result)

        if len(data) < window:
            data.append(init_altitude)
        
        ma = moving_average(data, window)
        ma = np.array(ma)

        estimated = ma[-1]
        estimated = (1 - alpha) * estimated + alpha * result
        var = np.var(data[-window:])
        var = (1 - beta) * var + beta * abs(result - estimated)
        
        print("Calibration Altitude: ", cali_altitude)
        
        if cali_altitude >= 0.5:
            try:
                pwm.ChangeDutyCycle(12.5)
                time.sleep(1)
                pwm.ChangeDutyCycle(2.5)
                time.sleep(0.7)
            except KeyboardInterrupt:
                pass
        
        if not abs(cali_altitude - estimated) <= np.sqrt(var):
            pwm.ChangeDutyCycle(0)
            init_altitude = 0
        
        with open('log_data.txt', 'a') as file:
            file.write(f'Calibration Altitude: {cali_altitude} m\n')
            file.flush()
            time.sleep(0.1)
        
        # time.sleep(0.3)
