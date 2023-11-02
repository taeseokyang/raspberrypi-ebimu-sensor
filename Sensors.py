import time
import board
import adafruit_bmp280
import RPi.GPIO as GPIO
import numpy as np
import serial
import datetime
import multiprocessing
import sys

#이동 평균 함수
def moving_average(data, window):
    moving_avg = data[:window] # 윈도우 이하의 데이터는 그냥 넣음.
    for i in range(window,len(data)):
        partial_avg = np.mean(data[i - window + 1 : i + 1]) # 이동 평균 계산
        moving_avg.append(partial_avg) # 추가
    return moving_avg 

# EBIMU 프로세스
def ebimu_process(n):
    # EBIMU 센서 값 저장 파일 이름 생성(당시 시간으로 파일 이름)
    nowTime = str(datetime.datetime.now())
    fileName = nowTime[:10]+"_ebimu_"+nowTime[11:21]
    # 파일 열기
    try:
        f = open(fileName, 'w')
        log = open("log.txt",'w')
    except:
        print("Failed to open file, EBIMU")
        sys.exit() #파일 열기가 실패했다면 강제 종료
        
    # 시리얼 통신 연결
    ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.001)

    # 버퍼 생성
    buf = "" 
    while True:
        # 센서 값이 들어왔다면 반복
        while ser.inWaiting():
            data = str(ser.read()).strip() # 데이터 입력
            buf += data # 버퍼링(buf변수에 계속 연결)
            if data[3] == "n": # 만약 b'n'데이터가 들어왔다면, 데이터 추출 시작
                # buf에는 "b'0'b'1'b'2'"과 같이 저장 되어 있음, '과 b를 없에줌.
                buf = buf.replace("'","")
                buf = buf.replace("b","") 
            
                # 데이터 파싱
                try : roll, pitch, yaw, x, y, z = map(float,buf[1:-4].split(','))
                except Exception as e:
                    print("Error from data processing : ", e)
                    log.write("Error from data processing : "+str(e)+"\n")
                    buf = ""
                    continue
                
                # 파일에 기록
                datas = [roll,pitch,yaw,x,y,z]
                writeString = "*"+str(datas)[1:-1]+"\n"
                f.write(writeString)
                
                # 출력
                print(roll,pitch,yaw,x,y,z)
                buf = ""

# 프로그램 시작 지점
if __name__ == '__main__':
    # EBIMU 프로세스 시작
    eb_p = multiprocessing.Process(target=ebimu_process, args=(1,))
    eb_p.start()

    #Bmp280 센서 연결
    i2c = board.I2C()  
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    bmp280.sea_level_pressure = 1019.5 

    #서보 모터 설정
    GPIO.setmode(GPIO.BCM)#핀 모드 설정
    servo_pin = 18
    GPIO.setwarnings(False)
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(2.5) 
    ##################################
    # 서보 동작 테스트 코드 추가 공간
    ##################################

    # 이동 평균 관련 변수
    window = 3 
    data = []
    moving_std = []
    alpha = 0.25
    beta = 0.125
    temp_altitude = []
    init_altitude = 0  
    
    #BMP데이터 파일과 서보 로그 파일 열기
    now = str(datetime.datetime.now())
    fileN = now[:10]+"_bmp_"+now[11:21]
    fileS = now[:10]+"_servoLog_"+now[11:21]
    try:
       f = open(fileN, 'w')
       s = open(fileS, 'w')
    except:
       print("Failed to open file, bmp")
       sys.exit() #파일 열기가 실패했다면 강제 종료
       

    #Bmp280
    while True:
        altitude = bmp280.altitude # 글로벌 고도 값 가져오기
        if init_altitude == 0: 
            init_altitude = altitude # 캘리브레이션 수행
        cali_altitude = altitude - init_altitude # 로컬 고도 계산
        result = cali_altitude
        data.append(result) # 데이터 리스트에 추가

        if len(data) < window: 
            data.append(init_altitude) # 데이터의 개수가 윈도우 보다 작다면 글로벌 고도 추가
        
        ma = moving_average(data, window) # 이동 평균 리스트 반환
        ma = np.array(ma) # 넘파이 배열로 변환

        # 낙하산 사출 조건 계산
        estimated = ma[-1] 
        estimated = (1 - alpha) * estimated + alpha * result
        var = np.var(data[-window:])
        var = (1 - beta) * var + beta * abs(result - estimated)

        # 낙하산 사출 조건 검사
        if abs(cali_altitude - estimated) <= np.sqrt(var):
            if cali_altitude > 0.5: # 최소 고도 보다 높다면 낙하산 사출
                try:
                    # 서보 동작
                    pwm.ChangeDutyCycle(7.5)
                    time.sleep(0.5)
                    pwm.ChangeDutyCycle(2.5)
                    time.sleep(0.5)
                    # 서보 동작 저장
                    s.write(f"{datetime.datetime.now()} Servo open log: {cali_altitude} m\n")
                except KeyboardInterrupt:
                    GPIO.cleanup()
                    # pass

        # 로컬 고도 출력
        print("Calibration Altitude: ", cali_altitude)
        # 로컬 고도 데이터 저장
        f.write(f"Calibration altitude: {cali_altitude} m\n")

#파일 열기 예외 처리에 강제 종료가 있어야 된다 생각함.
#서보를 열기만 하면 되는 건 아닌지
#해수면 기압 데이터는 항상 같은 값으로 넣는것인지
# cali_altitude와 result 같은 데이터인데 하나로 통일 하면 안될지
