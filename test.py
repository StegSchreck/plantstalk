#!/usr/bin/python

import signal
import time

import smbus
import veml6075
import Adafruit_DHT
from Adafruit_BMP.BMP085 import BMP085

import ds18b20 as temperature_sensor
from RepeatedTimer import RepeatedTimer

# DHT22 humidity sensor #
dht_sensor = Adafruit_DHT.DHT22
gpio_input_pin_humidity_sensor_cold_spot = 5
gpio_input_pin_humidity_sensor_hot_spot = 13

# BMP180 air pressure sensor #
bmp_sensor = BMP085()

# VEML 6075 UVA / UVB sensor #
bus4 = smbus.SMBus(4)
uv_sensor = veml6075.VEML6075(i2c_dev=bus4)
uv_sensor.set_shutdown(False)
uv_sensor.set_high_dynamic_range(False)
uv_sensor.set_integration_time('100ms')


def measure_cold_spot():
    humidity, temperature = read_measurements_from_dht22(gpio_input_pin_humidity_sensor_cold_spot)
    print('measure_cold_spot', humidity, temperature)
    return humidity, temperature


def measure_hot_spot():
    humidity, temperature = read_measurements_from_dht22(gpio_input_pin_humidity_sensor_hot_spot)

    print('measure_hot_spot', humidity, temperature)
    return humidity, temperature


def read_measurements_from_dht22(gpio_pin):
    print('read_measurements_from_dht22', gpio_pin)
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio_pin)
    print(gpio_pin, humidity, temperature)
    if not humidity or not temperature:
        return read_measurements_from_dht22(gpio_pin)
    return humidity, temperature


def measure_room_temperature():
    room_temperature = temperature_sensor.read()
    if not room_temperature:
        return measure_room_temperature()
    print('measure_room_temperature', room_temperature)
    return room_temperature


def measure_pressure():
    pressure = bmp_sensor.read_pressure()
    if not pressure:
        return measure_pressure()
    print('measure_pressure', pressure)
    return pressure


def measure_uv_light():
    uva, uvb = uv_sensor.get_measurements()
    uv_comp1, uv_comp2 = uv_sensor.get_comparitor_readings()
    uv_indices = uv_sensor.convert_to_index(uva, uvb, uv_comp1, uv_comp2)
    uva_index = uv_indices[0]
    uvb_index = uv_indices[1]
    avg_uv_index = uv_indices[2]
    print('measure_uv_light', uva, uvb, uva_index, uvb_index, avg_uv_index, uv_comp1, uv_comp2)
    return uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index


def measure():
    print('measure')
    cold_spot_humidity, cold_spot_temperature = measure_cold_spot()
    hot_spot_humidity, hot_spot_temperature = measure_hot_spot()
    room_temperature = measure_room_temperature()
    pressure = measure_pressure()
    uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index = measure_uv_light()


def main():
    print('main')
    temperature_sensor.setup()

    while True:
        measure()
        time.sleep(10)


if __name__ == '__main__':
    main()
