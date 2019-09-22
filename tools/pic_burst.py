#!/usr/bin/env python3

"""
Small script to take a burst of picture.
"""

import asyncio
import datetime

from picamera import PiCamera
from time import sleep
from os.path import join


camera = PiCamera()
camera.rotation = 180

FOLDER = "/home/pi/Pictures"

camera.start_preview()
sleep(3)

for i in range(20):

    time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    print(time)
    fname = f"burst_{time}_{i}.jpg"
    fpath = join(FOLDER, fname)
    camera.capture(fpath)
    sleep(1)

camera.stop_preview()

