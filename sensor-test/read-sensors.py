#!/usr/bin/env python

import time
from datetime import datetime
import Adafruit_DHT
from bmp280 import BMP280
from pms7003 import Pms7003Sensor, PmsSensorException
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

print("""Displays the reading from all sensors.
Press Ctrl+C to exit!
""")

# Initialise the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

# Initialise PMS7003
pms7003 = Pms7003Sensor('/dev/serial0')

# Initialise DHT11
dht11 = Adafruit_DHT.DHT11
dht11_gpio = 22

try:

    while True:
        print('--------------- {} ---------------'.format(
            datetime.now().strftime("%Y-%b-%d (%H:%M:%S)")))
        print('------------------------------------------------------')
        try:
            print('BMP280:')
            print('\t\tTemp = {:0.1f}*C'.format(bmp280.get_temperature()))
            print('\t\tPressure = {:05.2f}hPa'.format(bmp280.get_pressure()))
        except:
            print('Connection problem with BMP280')

        try:
            humidity, temperature = Adafruit_DHT.read_retry(dht11, dht11_gpio)
            print('DHT11:')
            if humidity is not None and temperature is not None:
                print('\t\tTemp = {:0.0f}*C'.format(temperature))
                print('\t\tHumidity = {:0.0f}%'.format(humidity))
            else:
                print('Failed to get reading. Try again!')
        except:
            print('Connection problem with DHT11')

        try:
            aqData = pms7003.read()
            print('PMS7003:')
            print('\t\tPM1.0_CF1 = {}'.format(aqData["pm1_0cf1"]))
            print('\t\tPM2.5_CF1 = {}'.format(aqData["pm2_5cf1"]))
            print('\t\tPM10_CF1 = {}'.format(aqData["pm10cf1"]))
            print('\t\tPM1.0 = {}'.format(aqData["pm1_0"]))
            print('\t\tPM2.5 = {}'.format(aqData["pm2_5"]))
            print('\t\tPM10 = {}'.format(aqData["pm10"]))
            print('\t\tPM_COUNT_0.3 = {}'.format(aqData["n0_3"]))
            print('\t\tPM_COUNT_0.5 = {}'.format(aqData["n0_5"]))
            print('\t\tPM_COUNT_1.0 = {}'.format(aqData["n1_0"]))
            print('\t\tPM_COUNT_2.5 = {}'.format(aqData["n2_5"]))
            print('\t\tPM_COUNT_5.0 = {}'.format(aqData["n5_0"]))
            print('\t\tPM_COUNT_10.0 = {}'.format(aqData["n10"]))
        except PmsSensorException:
            print('Connection problem with PMS7003')

        print('------------------------------------------------------')

        time.sleep(5)

except KeyboardInterrupt:
    print('Stopping sensors')
    pms7003.close()
