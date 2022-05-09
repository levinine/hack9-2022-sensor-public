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

## Running SSH tunnel localproxy listening process

```bash
python sensor_tunnel.py
```

## Running SSH tunnel localproxy listening process in background

```bash
nohup python sensor_tunnel.py > sensor_tunnel.log 2> sensor_tunnel.err < /dev/null &
```

## Setup sensor to start on boot

- Open crontab as root with nano
- ```sudo crontab -e```
- Add bellow line
- ```@reboot sleep 20; /usr/bin/python /home/pi/sensor/sensor-app/sensor.py > /home/pi/sensor/sensor-app/sensor.log 2>/home/pi/sensor/sensor-app/sensor.err &```

<https://github.com/aws-samples/aws-iot-securetunneling-localproxy>

## Opening SSH connection

- Create AWS IoT tunnel in AWS Console
- Choose thing to which you want to SSH
- Add new SSH service
- Configure tunnel timeout (optional)
- Run localproxy on your local machine and provide tunnels source token (<https://github.com/aws-samples/aws-iot-securetunneling-localproxy>), you can also use docker
  - localproxy -r {aws_region} -s 5555 -b 0.0.0.0 -t {token}
- SSH
