#!/usr/bin/python

import signal

import smbus
import veml6075
import Adafruit_DHT
from Adafruit_BMP.BMP085 import BMP085
from influxdb import InfluxDBClient

import ds18b20 as temperature_sensor
from RepeatedTimer import RepeatedTimer

# DHT22 humidity sensor #
dht_sensor = Adafruit_DHT.DHT22
gpio_input_pin_humidity_sensor_cold_spot = 5
gpio_input_pin_humidity_sensor_hot_spot = 19

# BMP180 air pressure sensor #
bmp_sensor = BMP085()

# VEML 6075 UVA / UVB sensor #
bus4 = smbus.SMBus(4)
uv_sensor = veml6075.VEML6075(i2c_dev=bus4)
uv_sensor.set_shutdown(False)
uv_sensor.set_high_dynamic_range(False)
uv_sensor.set_integration_time('100ms')

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
            "uv_comp1": 0.0,
            "uv_comp2": 0.0,
            "uva_index": 0.0,
            "uvb_index": 0.0,
            "avg_uv_index": 0.0,
        }
    }
]


def measure_cold_spot():
    return read_measurements_from_dht22(gpio_input_pin_humidity_sensor_cold_spot)


def measure_hot_spot():
    return read_measurements_from_dht22(gpio_input_pin_humidity_sensor_hot_spot)


def read_measurements_from_dht22(gpio_pin):
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio_pin)
    if not humidity or not temperature:
        return read_measurements_from_dht22(gpio_pin)
    return humidity, temperature


def measure_room_temperature():
    room_temperature = temperature_sensor.read()
    if not room_temperature:
        return measure_room_temperature()
    return room_temperature


def measure_pressure():
    pressure = bmp_sensor.read_pressure()
    if not pressure:
        return measure_pressure()
    return pressure


def measure_uv_light():
    uva, uvb = uv_sensor.get_measurements()
    uv_comp1, uv_comp2 = uv_sensor.get_comparitor_readings()
    uv_indices = uv_sensor.convert_to_index(uva, uvb, uv_comp1, uv_comp2)
    uva_index = uv_indices[0]
    uvb_index = uv_indices[1]
    avg_uv_index = uv_indices[2]
    return uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index


def send_measurements(cold_spot_humidity, cold_spot_temperature, hot_spot_humidity, hot_spot_temperature, room_temperature, pressure, uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index):
    if 0 <= cold_spot_humidity <= 100:
        json_body[0]['fields']['cold_spot_humidity'] = float(cold_spot_humidity)
    else:
        json_body[0]['fields'].pop('cold_spot_humidity', 0)

    if 0 <= cold_spot_temperature <= 100:
        json_body[0]['fields']['cold_spot_temperature'] = float(cold_spot_temperature)
    else:
        json_body[0]['fields'].pop('cold_spot_temperature', 0)

    if 0 <= hot_spot_humidity <= 100:
        json_body[0]['fields']['hot_spot_humidity'] = float(hot_spot_humidity)
    else:
        json_body[0]['fields'].pop('hot_spot_humidity', 0)

    if 0 <= hot_spot_temperature <= 100:
        json_body[0]['fields']['hot_spot_temperature'] = float(hot_spot_temperature)
    else:
        json_body[0]['fields'].pop('hot_spot_temperature', 0)

    json_body[0]['fields']['room_temperature'] = room_temperature
    json_body[0]['fields']['pressure'] = pressure
    json_body[0]['fields']['uva'] = uva
    json_body[0]['fields']['uvb'] = uvb
    json_body[0]['fields']['uv_comp1'] = uv_comp1
    json_body[0]['fields']['uv_comp2'] = uv_comp2
    json_body[0]['fields']['uva_index'] = uva_index
    json_body[0]['fields']['uvb_index'] = uvb_index
    json_body[0]['fields']['avg_uv_index'] = avg_uv_index
    client.write_points(json_body)


def measure():
    cold_spot_humidity, cold_spot_temperature = measure_cold_spot()
    hot_spot_humidity, hot_spot_temperature = measure_hot_spot()
    room_temperature = measure_room_temperature()
    pressure = measure_pressure()
    uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index = measure_uv_light()
    send_measurements(cold_spot_humidity, cold_spot_temperature, hot_spot_humidity, hot_spot_temperature, room_temperature, pressure, uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index)


def main():
    temperature_sensor.setup()

    RepeatedTimer(10, measure)

    while True:
        signal.pause()


if __name__ == '__main__':
    main()
