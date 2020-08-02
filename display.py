#!/usr/bin/env python
import signal

from LCD1602 import LCD
from influxdb import InfluxDBClient

from RepeatedTimer import RepeatedTimer

# InfluxDB #
influx_host_ip = '127.0.0.1'
influx_host_port = 8086
influx_db = 'plantstalk'
client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)
client.switch_database(influx_db)

lcd = LCD(i2c_addr=0x27)  # params available for rPi revision, I2C Address, and backlight on/off


def read_data_from_database():
    return client.query('SELECT MEAN("cold_spot_temperature") as cold_spot_temperature, '
                        '       MEAN("cold_spot_humidity") as cold_spot_humidity, '
                        '       MEAN("hot_spot_temperature") as hot_spot_temperature, '
                        '       MEAN("hot_spot_humidity") as hot_spot_humidity'
                        'FROM "plantstalk"."autogen"."plantstalk" '
                        'WHERE time >= now() - 5m')


def display():
    result = read_data_from_database()
    values = [value for value in result.get_points(measurement=influx_db)]
    lcd.clear()

    hot_spot_temperature = values[0]['hot_spot_temperature']
    hot_spot_humidity = values[0]['hot_spot_humidity']
    lcd.message("Warm {}° {}%".format(round(hot_spot_temperature, 1), round(hot_spot_humidity, 1)), 1)

    cold_spot_temperature = values[0]['cold_spot_temperature']
    cold_spot_humidity = values[0]['cold_spot_humidity']
    lcd.message("Kalt {}° {}%".format(round(cold_spot_temperature, 1), round(cold_spot_humidity, 1)), 2)


def main():
    lcd.message("Initializing ...", 1)

    RepeatedTimer(30, display)

    while True:
        signal.pause()


if __name__ == '__main__':
    main()
