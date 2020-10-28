#!/usr/bin/env python3

"""
Small script to take small burst of pictures on a regular basis over a long period of time.
"""

import asyncio
import datetime
import typer

from picamera import PiCamera
from time import sleep
from os.path import join


async def take_pic(camera, out, cycles, burst, delay, prefix, warmup):

    for j in range(cycles):

        camera.start_preview()
        await asyncio.sleep(warmup)

        for i in range(burst):
            time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            fname = f"{prefix}{time}_{i}.jpg"
            fpath = join(out, fname)
            camera.capture(fpath)
            await asyncio.sleep(1)

        camera.stop_preview()
        await asyncio.sleep(delay)


def main(out: str = ".", cycles: int = 144, burst: int = 3, delay: int = 600, prefix: str = "img_", warmup: int = 3, rotation: int = 0):
    with PiCamera() as camera:
        camera.rotation = rotation
        loop = asyncio.get_event_loop()
        loop.run_until_complete(take_pic(camera, out, cycles, burst, delay, prefix, warmup))

        
if __name__ == "__main__":
    typer.run(main)
    
