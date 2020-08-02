#!/usr/bin/env python
import datetime
import signal

import pytz
from astral import location
from astral.sun import sun
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

from RepeatedTimer import RepeatedTimer

# InfluxDB #
influx_host_ip = '127.0.0.1'
influx_host_port = 8086
influx_db = 'plantstalk'
influx_client = InfluxDBClient(influx_host_ip, influx_host_port, influx_db)

# MQTT #
mqtt_client = mqtt.Client()
mqtt_client.connect("192.168.178.29", 1883, 60)

ON = "ON"
OFF = "OFF"
TOPIC_COMMAND_TERRARIUM_SPOT_POWER = "cmnd/Terrarium_1/POWER"
TOPIC_COMMAND_TERRARIUM_UV_POWER = "cmnd/Terrarium_2/POWER"
TOPIC_COMMAND_TERRARIUM_HUMIDIFIER_POWER = "cmnd/Terrarium_3/POWER"

location = location.LocationInfo('Berlin', 'Deutschland', 'Europe/Berlin', 52.530209, 13.363372)
timezone = pytz.timezone('Europe/Berlin')

#                          Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
desired_temperature_min = [17.9, 17.8, 18.7, 19.8, 21.1, 22.7, 23.4, 23.8, 23.5, 22.2, 20.0, 19.4]
desired_temperature_max = [24.2, 24.5, 25.6, 26.4, 27.6, 29.1, 29.4, 29.9, 29.2, 28.1, 26.1, 25.3]
#                          Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
desired_humidity =        [67.4, 67.9, 68.2, 67.0, 68.5, 71.5, 72.4, 73.4, 75.1, 74.1, 69.5, 72.0]
desired_humidity_min = 65
desired_humidity_max = 80

# desired_sun_hours = [9, 10, 11, 12, 12.5, 13, 13, 12.5, 12, 11, 10, 9]


def read_data_from_database():
    return influx_client.query('SELECT MEAN("cold_spot_temperature") as cold_spot_temperature, '
                               '       MEAN("cold_spot_humidity") as cold_spot_humidity, '
                               '       MEAN("hot_spot_humidity") as hot_spot_humidity, '
                               '       MEAN("hot_spot_humidity") as hot_spot_humidity '
                               'FROM "plantstalk"."autogen"."plantstalk" '
                               'WHERE time >= now() - 10m')


def control():
    result = read_data_from_database()
    values = [value for value in result.get_points(measurement=influx_db)]
    now = datetime.datetime.now(tz=timezone)
    sun_movement = sun(location.observer, date=now, tzinfo=location.timezone)

    cold_spot_temperature = values[0]['cold_spot_temperature']
    cold_spot_humidity = values[0]['cold_spot_humidity']
    hot_spot_temperature = values[0]['hot_spot_temperature']
    hot_spot_humidity = values[0]['hot_spot_humidity']

    is_daylight = sun_movement['sunrise'] < now < sun_movement['sunset']
    is_temperature_ok = desired_temperature_min[now.month] <= cold_spot_temperature \
                        <= hot_spot_temperature <= desired_temperature_max[now.month]
    is_humidity_ok = desired_humidity_min <= cold_spot_humidity <= hot_spot_humidity <= desired_humidity_max

    if is_daylight:
        print('daylight')

    # mqtt_client.publish(TOPIC_COMMAND_TERRARIUM_SPOT_POWER, ON)
    # mqtt_client.publish(TOPIC_COMMAND_TERRARIUM_SPOT_POWER, ON)


def main():
    influx_client.switch_database(influx_db)

    RepeatedTimer(30, control)

    while True:
        signal.pause()

    mqtt_client.disconnect()


if __name__ == '__main__':
    main()
