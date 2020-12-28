#!/usr/bin/python

import board
import busio

import adafruit_veml6075
import adafruit_dht
import ds18b20 as temperature_sensor

# DHT22 humidity & temperature sensor #
dht_cold_spot = adafruit_dht.DHT22(board.D5)
dht_hot_spot = adafruit_dht.DHT22(board.D13)

# BMP180 air pressure sensor #
# bmp_sensor = BMP085()

# VEML 6075 UVA / UVB sensor #
i2c = busio.I2C(board.SCL, board.SDA)
veml6075 = adafruit_veml6075.VEML6075(i2c, integration_time=100)


def measure_cold_spot():
    temperature = dht_cold_spot.temperature
    humidity = dht_cold_spot.humidity
    print('measure_cold_spot', humidity, temperature)
    return humidity, temperature


def measure_hot_spot():
    temperature = dht_hot_spot.temperature
    humidity = dht_hot_spot.humidity
    print('measure_hot_spot', humidity, temperature)
    return humidity, temperature


def measure_room_temperature():
    room_temperature = temperature_sensor.read()
    print('measure_room_temperature', room_temperature)
    return room_temperature


def measure_pressure():
    # pressure = bmp_sensor.read_pressure()
    # print('measure_pressure', pressure)
    return None


def measure_uv_light():
    print('measure_uv_light', veml6075.uva, veml6075.uvb, veml6075.uv_index)
    return veml6075.uva, veml6075.uvb, veml6075.uv_index


def measure():
    print('Start measuring...')
    room_temperature = measure_room_temperature()
    pressure = measure_pressure()
    cold_spot_humidity, cold_spot_temperature = measure_cold_spot()
    hot_spot_humidity, hot_spot_temperature = measure_hot_spot()
    uva, uvb, avg_uv_index = measure_uv_light()


def main():
    print('main')
    temperature_sensor.setup()

    measure()


if __name__ == '__main__':
    main()
