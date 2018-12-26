# Plantstalk
Forked from [Sh4kE/plantstalk](https://github.com/Sh4kE/plantstalk).

## Setup TICK + Grafana stack
About the TICK stack: https://www.influxdata.com/time-series-platform/
Setup guide: https://canox.net/2018/01/installation-von-grafana-influxdb-telegraf-auf-einem-raspberry-pi/
In IndluxDB: create Database `plantstalk`
In Grafana: create data source for that table

## Install Requirements
### Adafruit DHT for humidity sensor
```bash
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
```

### Adafruit BMP for air pressure sensor
```bash
git clone https://github.com/adafruit/Adafruit_Python_BMP.git
cd Adafruit_Python_BMP
sudo python3 setup.py install
```

## Setup Measurements
```bash
git clone https://github.com/StegSchreck/plantstalk.git
cd plantstalk
pip3 install -r requirements.txt
sudo apt install python3-smbus
python3 ./plantstalk.py
```

### Alternative: Install Systemd Unit
```bash
sudo ln -s <plantstalk_repo>/plantstalk.service /etc/systemd/system/plantstalk.service  # install the service
sudo systemctl start plantstalk
sudo systemctl enable plantstalk  # make it reboot-safe 
```

## Apache configuration
* Request SSL certificate with Let'sEncrypt
    * https://tutorials-raspberrypi.de/raspberry-pi-ssl-zertifikat-kostenlos-mit-lets-encrypt-erstellen/ (german)
* Install Apache webserver and necessary mods
    ```bash
    sudo apt install apache2 
    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo a2enmod rewrite
    sudo systemctl restart apache2
    ```
* Add configuration for Grafana
    ```bash
    sudo cp <plantstalk_repo>/grafana.conf /etc/apache2/sites-available
    sudo cd /etc/apache2/sites-enabled
    sudo ln -s ../sites-available/grafana.conf grafana.conf
    sudo systemctl reload apache2
    ```
