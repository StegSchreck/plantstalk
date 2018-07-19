#!/usr/bin/python

import time

from picamera import PiCamera
from time import sleep

from RepeatedTimer import RepeatedTimer


def take_image():
    with PiCamera(resolution=(2592, 1944)) as camera:
        sleep(2)
        name = 'screenshot.jpg'
        camera.capture(name)


def main():
    camera_timer = RepeatedTimer(60, take_image)

    while True:
        camera_timer.start()
        time.sleep(60)


if __name__ == '__main__':
    main()
