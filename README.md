# Plantstalk
Forked from [Sh4kE/plantstalk](https://github.com/Sh4kE/plantstalk).

## Setup TICK + Grafana stack
About the TICK stack: https://www.influxdata.com/time-series-platform/
Setup guide: https://canox.net/2018/01/installation-von-grafana-influxdb-telegraf-auf-einem-raspberry-pi/
In IndluxDB: create Database `plantstalk`
In Grafana: create data source for that table

## Install Requirements
```
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
```

## Setup Measurements
```
git clone https://github.com/StegSchreck/plantstalk.git
cd plantstalk
pip3 install -r requirements.txt
sudo apt install python3-smbus
python3 ./plantstalk.py
```
