#!/usr/bin/env python3

"""
Small script to take pictures on a regular basis.
"""

import asyncio

from picamera import PiCamera
from time import sleep
from os.path import join


camera = PiCamera()
camera.rotation = 180

FOLDER = "/home/pi/Pictures"

async def take_pic():

    while True:
        for i in range(5):

            time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"img_{i}_{time}.jpg"
            fpath = join(FOLDER, fname)

            camera.start_preview()
            #sleep(5)
            asyncio.sleep(5)
            camera.capture(fpath)
            camera.stop_preview()

        asyncio.sleep(5*60)

loop = asyncio.get_event_loop()
loop.run(take_pic())
