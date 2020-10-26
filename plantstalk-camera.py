#!/usr/bin/python
import os
import time
from datetime import datetime
from time import sleep

from picamera import PiCamera

folder_for_images = "/home/pi/picures/plantstalk"
interval_between_images_in_seconds = 20
start_hour_in_the_evening = 21
end_hour_in_the_morning = 8

# /opt/vc/bin/raspivid -o - -t 0 -hf -w 640 -h 360 -fps 25|cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264


def take_image():
    with PiCamera(resolution=(2592, 1944)) as camera:
        sleep(2)
        if not os.path.exists(folder_for_images):
            os.makedirs(folder_for_images)
        filename = datetime.now().strftime('plantstalk_%Y-%m-%d_%H-%M-%S.jpg')
        camera.capture(os.path.join(folder_for_images, filename))


def main():
    while True:
        is_nighttime = not end_hour_in_the_morning <= datetime.now().hour < start_hour_in_the_evening
        if is_nighttime:
            take_image()
        time.sleep(interval_between_images_in_seconds)


if __name__ == '__main__':
    main()
