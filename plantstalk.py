#!/usr/bin/python

import signal

import Adafruit_DHT
from influxdb import InfluxDBClient

from RepeatedTimer import RepeatedTimer

# DHT11 Sensor #
from mq import MQ

dht_sensor = Adafruit_DHT.DHT11
gpio_input_pin = 19
mq = MQ(analogPin=22)

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
            "lpg": 0.0,
            "carbon_oxide": 0.0,
            "smoke": 0.0,
        }
    }
]


def measure_humidity_and_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, gpio_input_pin)
    if not humidity or not temperature:
        return measure_humidity_and_temperature()
    return humidity, temperature


def send_measurements(client, humidity, temperature, lpg, carbon_oxide, smoke):
    json_body[0]['fields']['temperature'] = temperature
    if 0 <= humidity <= 100:
        json_body[0]['fields']['humidity'] = humidity
    else:
        json_body[0]['fields'].pop('humidity', 0)
    json_body[0]['fields']['lpg'] = lpg
    json_body[0]['fields']['carbon_oxide'] = carbon_oxide
    json_body[0]['fields']['smoke'] = smoke
    client.write_points(json_body)


def measure(client):
    humidity, temperature = measure_humidity_and_temperature()
    gas_measurement_result = mq.MQPercentage()
    lpg = gas_measurement_result["GAS_LPG"]
    carbon_oxide = gas_measurement_result["CO"]
    smoke = gas_measurement_result["SMOKE"]
    send_measurements(client, humidity, temperature, lpg, carbon_oxide, smoke)


def main():
    client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)
    client.switch_database(influx_db)

    RepeatedTimer(10, measure, client)

    while True:
        signal.pause()


if __name__ == '__main__':
    main()
