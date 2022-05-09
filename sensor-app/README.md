# A python app for PMS7003 BMP280 DHT11 sensor reading and sending to AWS IoT and Azure IoT Hub

## Installing Dependencies

```bash
sudo apt install libgpiod2
sudo -H pip3 install adafruit-circuitpython-pm25
sudo -H pip3 install pms7003
sudo -H pip3 install adafruit-circuitpython-bmp280
sudo -H pip3 install adafruit-circuitpython-dht
sudo -H pip3 install AWSIoTPythonSDK
sudo -H pip3 install dynaconf[all]
sudo -H pip3 install azure-iot-device
```

## Running

```bash
python sensor.py
```

## Running in background

```bash
nohup python sensor.py > sensor.log 2> sensor.err < /dev/null &
```

## Setup sensor to start on boot

- Open crontab as root with nano
- ```sudo crontab -e```
- Add bellow line
- ```@reboot sleep 20; /usr/bin/python /home/pi/sensor/sensor-app/sensor.py > /home/pi/sensor/sensor-app/sensor.log 2>/home/pi/sensor/sensor-app/sensor.err &```
