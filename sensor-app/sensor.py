#!/usr/bin/env python

import adafruit_bmp280
import adafruit_dht
from adafruit_pm25.uart import PM25_UART
from pms7003 import Pms7003Sensor, PmsSensorException
import board

import uuid
import json
import serial
import time
from datetime import datetime
from dynaconf import settings

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from azure.iot.device import IoTHubDeviceClient, Message

print("Initializing sensors...")
# reset_pin = None
# uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.25)
pms7003 = Pms7003Sensor('/dev/serial0')

i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
bmp280.sea_level_pressure = 1016.4

dht11 = adafruit_dht.DHT11(22)
print("Sensors initialized.")

print("Connecting to AWS IoT...")
endpoint = settings.get('aws_endpoint')
rootCAPath = settings.get('aws_rootCAPath')
certificatePath = settings.get('aws_certificatePath')
privateKeyPath = settings.get('aws_privateKeyPath')
port = settings.get('aws_port')
useWebsocket = settings.as_bool('aws_useWebsocket')
clientId = settings.get('aws_clientId')
topic = settings.get('aws_topic')

airAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
airAWSIoTMQTTClient.configureEndpoint(endpoint, port)
airAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

airAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
airAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
airAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
airAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
airAWSIoTMQTTClient.configureMQTTOperationTimeout(30)  # 5 sec

airAWSIoTMQTTClient.connect()

print("Connected to AWS IoT.")

print("Connecting to Azure IoT Hub...")

azureIotConnStr = settings.get('azure_iot_connection_string')
ioTHubDeviceClient = IoTHubDeviceClient.create_from_connection_string(azureIotConnStr)

print("Connected to Azure IoT Hub.")

while True:
    print("Reading air quality measurements...")

    time.sleep(2)

    # pms7003 = PM25_UART(uart, reset_pin)
    air_quality_data = pms7003.read()
    # pm10 = air_quality_data["pm10 standard"]
    # pm25 = air_quality_data["pm25 standard"]
    # pm100 = air_quality_data["pm100 standard"]
    pm10 = air_quality_data["pm1_0"]
    pm25 = air_quality_data["pm2_5"]
    pm100 = air_quality_data["pm10"]

    temperature = bmp280.temperature + settings.get('sensor_temp_adjustment', 0)
    pressure = bmp280.pressure
    altitude = bmp280.altitude

    try:
        humidity = dht11.humidity + settings.get('sensor_humidity_adjustment', 0)
    except:
        print("DHT11 reading failed, retrying...")
        humidity = dht11.humidity + settings.get('sensor_humidity_adjustment', 0)

    # Print readings on the console

    print('-------------------------{}---------------------------'.format(datetime.now().strftime("%d.%b.%Y %H:%M:%S")))

    print("PMS7003 PM1: %0.1f" % pm10)
    print("PMS7003 PM2.5: %0.1f" % pm25)
    print("PMS7003 PM10: %0.1f" % pm100)

    print("BMP280 Temperature: %0.1f C" % temperature)
    print("BMP280 Pressure: %0.1f hPa" % pressure)
    print("BMP280 Altitude: %0.2f meters" % altitude)

    print("DHT11 Humidity: %0.1f" % humidity, '%')
    print("DHT11 Temperature: %0.1f" % dht11.temperature, 'C')
    print('------------------------------------------------------------------------')

    # Create message to send to AWS and Azure
    message = {
        "time": {
            "nano": time.time_ns()
        },
        "location": {
            "latitude": settings.get('sensor_location.latitude'),
            "longitude": settings.get('sensor_location.longitude'),
            "name": settings.get('sensor_location.name')
        },
        "name": settings.get('sensor_name'),
        "pms7003Measurement": {
            "pm10Atmo": pm10,
            "pm25Atmo": pm25,
            "pm100Atmo": pm100
        },
        "bmp280Measurement": {
            "temperature": temperature,
            "pressure": pressure
        },
        "dht11Measurement": {
            "humidity": humidity
        }
    }
    messageJson = json.dumps(message)

    print('Sending to AWS IoT...')

    try:
        airAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Sent to AWS IoT.')
    except:
        print("Failed sending to AWS IoT.")

    print('Sending to Azure IoT Hub...')

    msg = Message(messageJson)
    msg.message_id = uuid.uuid4()
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    try:
        ioTHubDeviceClient.send_message(msg)
        print('Sent to Azure IoT Hub.')
    except:
        print("Failed sending to Azure IoT Hub.")

    time.sleep(settings.get('sensor_interval'))
