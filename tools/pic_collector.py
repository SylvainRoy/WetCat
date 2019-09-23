#!/usr/bin/env python3

"""
Small script to take pictures on a regular basis.
"""

import asyncio
import datetime

from picamera import PiCamera
from time import sleep
from os.path import join


FOLDER = "/home/pi/Pictures"


async def take_pic(camera):

    for j in range(1000):
        camera.start_preview()
        await asyncio.sleep(5)

        for i in range(3):
            time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            fname = f"img_{time}_{i}.jpg"
            fpath = join(FOLDER, fname)
            camera.capture(fpath)
            await asyncio.sleep(2)

        camera.stop_preview()
        await asyncio.sleep(10*60)


with PiCamera() as camera:
    camera.rotation = 180
    loop = asyncio.get_event_loop()
    loop.run_until_complete(take_pic(camera))
