#!/usr/bin/python
import os
import shutil
import time
from datetime import datetime
from time import sleep

from picamera import PiCamera

folder_for_images = "/home/pi/pictures/plantstalk"
interval_between_images_in_seconds = 1
start_hour_in_the_evening = 22
end_hour_in_the_morning = 8

# /opt/vc/bin/raspivid -o - -t 0 -hf -w 640 -h 360 -fps 25|cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264


def take_image():
    with PiCamera(resolution=(2592, 1944)) as camera:
        sleep(1)
        if not os.path.exists(folder_for_images):
            # print('creating target folder as it is not present:', folder_for_images)
            os.makedirs(folder_for_images)
        filename = datetime.now().strftime('plantstalk_%Y-%m-%d_%H-%M-%S.jpg')
        picture_file_location_for_timelapse = os.path.join(folder_for_images, filename)
        picture_file_location_for_server = os.path.join('/home/pi/pictures', 'index.jpg')

        camera.capture(picture_file_location_for_server)

        is_nighttime = not end_hour_in_the_morning <= datetime.now().hour < start_hour_in_the_evening
        # print(end_hour_in_the_morning, datetime.now().hour, start_hour_in_the_evening, is_nighttime)
        if is_nighttime:
            # copy file over to specific directory for the timelapse creation next day
            shutil.copyfile(picture_file_location_for_server, picture_file_location_for_timelapse)
        # print('saved image', os.path.join(folder_for_images, filename))


def main():
    while True:
        take_image()
        time.sleep(interval_between_images_in_seconds)


if __name__ == '__main__':
    main()
