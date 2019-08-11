#!/usr/bin/python

import signal

import smbus
import veml6075
import Adafruit_DHT
from Adafruit_BMP.BMP085 import BMP085
from gpiozero import InputDevice
from influxdb import InfluxDBClient

import ds18b20 as temperature_sensor
from RepeatedTimer import RepeatedTimer
import GroveMultichannelGasSensor

# DHT22 humidity sensor #
dht_sensor = Adafruit_DHT.DHT22
gpio_input_pin_humidity_sensor = 5

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
json_body = [
    {
        "measurement": influx_db,
        "fields": {
            "temperature": 0.0,
            "humidity": 0.0,
            "pressure": 0.0,
            "rain": 0.0,
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


def measure_uv_light():
    uva, uvb = uv_sensor.get_measurements()
    uv_comp1, uv_comp2 = uv_sensor.get_comparitor_readings()
    uv_indices = uv_sensor.convert_to_index(uva, uvb, uv_comp1, uv_comp2)
    uva_index = uv_indices[0]
    uvb_index = uv_indices[1]
    avg_uv_index = uv_indices[2]
    return uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index


def measure_toxic_gases():
    gas_sensor = GroveMultichannelGasSensor.MutichannelGasSensor(address=0x10)
    ammonia = gas_sensor.readData(0x11)
    carbon_monoxide = gas_sensor.readData(0x12)
    nitrogen_dioxide = gas_sensor.readData(0x13)


def send_measurements(client, humidity, temperature, pressure, uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index):
    json_body[0]['fields']['temperature'] = temperature
    if 0 <= humidity <= 100:
        json_body[0]['fields']['humidity'] = float(humidity)
    else:
        json_body[0]['fields'].pop('humidity', 0)
    json_body[0]['fields']['pressure'] = pressure
    json_body[0]['fields']['uva'] = uva
    json_body[0]['fields']['uvb'] = uvb
    json_body[0]['fields']['uv_comp1'] = uv_comp1
    json_body[0]['fields']['uv_comp2'] = uv_comp2
    json_body[0]['fields']['uva_index'] = uva_index
    json_body[0]['fields']['uvb_index'] = uvb_index
    json_body[0]['fields']['avg_uv_index'] = avg_uv_index
    client.write_points(json_body)


def measure(client):
    humidity = measure_humidity()
    temperature = measure_temperature()
    pressure = measure_pressure()
    uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index = measure_uv_light()
    send_measurements(client, humidity, temperature, pressure, uva, uvb, uv_comp1, uv_comp2, uva_index, uvb_index, avg_uv_index)


def main():
    # client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)
    # client.switch_database(influx_db)
    # temperature_sensor.setup()
    #
    # RepeatedTimer(10, measure, client)
    measure_toxic_gases()

    # while True:
    #     signal.pause()


if __name__ == '__main__':
    main()
