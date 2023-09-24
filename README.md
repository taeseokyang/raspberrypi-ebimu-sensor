# raspberrypi-ebimu-sensor

## 센서 
EBIMU_9DOF
![KakaoTalk_Photo_2023-09-23-18-51-39](https://github.com/taeseokyang/arduino-ebimu-sensor/assets/136783693/c5f34991-6b49-4232-9669-e9451e0ed461)
<img width="423" alt="image" src="https://github.com/taeseokyang/arduino-ebimu-sensor/assets/136783693/c77a135e-a92b-49fd-aa26-529e0a934bb2">

## 설명
EBIMU_9DOFV2 센서를 이용한 roll,pitch,yaw 데이터를 Matplot 그래프로 시각화.</br>

## 회로

### case 1 - USB로 시리얼 통신
|Raspberry pi|센서|
|---|---|
|5V|VIN|
|GND|GND|
|RX(0)|TX|
|TX(1)|RX|

### case 2 - 4, 5번 핀으로 시리얼 통신
|Raspberry pi|센서|
|---|---|
|5V|VIN|
|GND|GND|
|RX(0)|TX|
|TX(1)|RX|

#### 시리얼 핀 설정 방법 
https://m.blog.naver.com/emperonics/222039301356




