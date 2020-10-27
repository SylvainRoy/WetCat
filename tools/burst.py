#!/usr/bin/env python3

"""
Small script to take a burst of pictures.
"""


import asyncio
import datetime
import typer

from picamera import PiCamera
from time import sleep
from os.path import join


def main(num: int = 5, out: str  = ".", rotation: int = 180, warmup: int = 3, delay: int = 1, prefix: str = "burst_"):
    
    with PiCamera() as camera:
        camera.rotation = rotation

        typer.echo("Starting camera")
        camera.start_preview()

        typer.echo("Warming up")
        sleep(warmup)

        for i in range(num):

            time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            fname = f"{prefix}{time}_{i}.jpg"
            fpath = join(out, fname)
            typer.echo(f"Pic {i}: {fpath}")
            camera.capture(fpath)
            sleep(delay)

        typer.echo("Stopping camera")
        camera.stop_preview()


if __name__ == "__main__":
    typer.run(main)

