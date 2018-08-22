#!/usr/bin/python
from builtins import float

import signal

import Adafruit_DHT
from Adafruit_BMP.BMP085 import BMP085
from gpiozero import InputDevice
from influxdb import InfluxDBClient

import ds18b20 as temperature_sensor
from RepeatedTimer import RepeatedTimer

# DHT22 humidity sensor #
dht_sensor = Adafruit_DHT.DHT22
gpio_input_pin_humidity_sensor = 5

# BMP180 air pressure sensor #
bmp_sensor = BMP085()

# InfluxDB #
influx_host_ip = '127.0.0.1'
influx_host_port = 8086
influx_db = 'plantstalk'
json_body = [
    {
        "measurement": influx_db,
        "fields": {
            "temperature": 0.0,
            "humidity": 0.0,
            "pressure": 0.0,
            "rain": 0.0,
        }
    }
]


def measure_humidity():
    humidity, _ = Adafruit_DHT.read_retry(dht_sensor, gpio_input_pin_humidity_sensor)
    if not humidity:
        return measure_humidity()
    return humidity


def measure_temperature():
    temperature = temperature_sensor.read()
    if not temperature:
        return measure_temperature()
    return temperature


def measure_pressure():
    pressure = bmp_sensor.read_pressure()
    if not pressure:
        return measure_pressure()
    return pressure


def measure_rain():
    rain_is_falling = InputDevice(18).is_active
    return 1.0 if rain_is_falling else 0.0


def send_measurements(client, humidity, temperature, pressure, rain):
    json_body[0]['fields']['temperature'] = temperature
    if 0 <= humidity <= 100:
        json_body[0]['fields']['humidity'] = float(humidity)
    else:
        json_body[0]['fields'].pop('humidity', 0)
    json_body[0]['fields']['pressure'] = pressure
    json_body[0]['fields']['rain'] = rain
    client.write_points(json_body)


def measure(client):
    humidity = measure_humidity()
    temperature = measure_temperature()
    pressure = measure_pressure()
    rain = measure_rain()
    send_measurements(client, humidity, temperature, pressure, rain)


def main():
    client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)
    client.switch_database(influx_db)
    temperature_sensor.setup()

    RepeatedTimer(10, measure, client)

    while True:
        signal.pause()


if __name__ == '__main__':
    main()