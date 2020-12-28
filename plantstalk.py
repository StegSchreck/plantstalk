#!/usr/bin/python

import signal

import board
import busio

import adafruit_veml6075
import adafruit_dht
import ds18b20 as temperature_sensor

from RepeatedTimer import RepeatedTimer
from influxdb import InfluxDBClient

# DHT22 humidity & temperature sensor #
dht_cold_spot = adafruit_dht.DHT22(board.D5)
dht_hot_spot = adafruit_dht.DHT22(board.D13)

# VEML 6075 UVA / UVB sensor #
i2c = busio.I2C(board.SCL, board.SDA)
veml6075 = adafruit_veml6075.VEML6075(i2c, integration_time=100)

# InfluxDB #
influx_host_ip = '127.0.0.1'
influx_host_port = 8086
influx_db = 'plantstalk'
client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)
client.switch_database(influx_db)
json_body = [
    {
        "measurement": influx_db,
        "fields": {
            "cold_spot_humidity": 0.0,
            "cold_spot_temperature": 0.0,
            "hot_spot_humidity": 0.0,
            "hot_spot_temperature": 0.0,
            "room_temperature": 0.0,
            "pressure": 0.0,
            "uva": 0.0,
            "uvb": 0.0,
        }
    }
]


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


def measure_uv_light():
    print('measure_uv_light', veml6075.uva, veml6075.uvb, veml6075.uv_index)
    return veml6075.uva, veml6075.uvb, veml6075.uv_index


def send_measurements(cold_spot_humidity, cold_spot_temperature, hot_spot_humidity, hot_spot_temperature, room_temperature, uva, uvb, avg_uv_index):
    print('Sending measurements to InfluxDB')

    if cold_spot_humidity and 0 <= cold_spot_humidity <= 100:
        json_body[0]['fields']['cold_spot_humidity'] = float(cold_spot_humidity)
    else:
        json_body[0]['fields'].pop('cold_spot_humidity', 0)

    if cold_spot_temperature and 0 <= cold_spot_temperature <= 100:
        json_body[0]['fields']['cold_spot_temperature'] = float(cold_spot_temperature)
    else:
        json_body[0]['fields'].pop('cold_spot_temperature', 0)

    if hot_spot_humidity and 0 <= hot_spot_humidity <= 100:
        json_body[0]['fields']['hot_spot_humidity'] = float(hot_spot_humidity)
    else:
        json_body[0]['fields'].pop('hot_spot_humidity', 0)

    if hot_spot_temperature and 0 <= hot_spot_temperature <= 100:
        json_body[0]['fields']['hot_spot_temperature'] = float(hot_spot_temperature)
    else:
        json_body[0]['fields'].pop('hot_spot_temperature', 0)

    json_body[0]['fields']['room_temperature'] = room_temperature
    json_body[0]['fields']['uva'] = uva
    json_body[0]['fields']['uvb'] = uvb
    json_body[0]['fields']['avg_uv_index'] = avg_uv_index

    client.write_points(json_body)


def measure():
    print('Start measuring...')
    room_temperature = measure_room_temperature()
    cold_spot_humidity, cold_spot_temperature = measure_cold_spot()
    hot_spot_humidity, hot_spot_temperature = measure_hot_spot()
    uva, uvb, avg_uv_index = measure_uv_light()
    send_measurements(cold_spot_humidity, cold_spot_temperature, hot_spot_humidity, hot_spot_temperature, room_temperature, uva, uvb, avg_uv_index)


def main():
    temperature_sensor.setup()

    RepeatedTimer(10, measure)

    while True:
        signal.pause()


if __name__ == '__main__':
    main()
