#!/usr/bin/env python3

"""
Takes a picture.
"""

import typer

from datetime import datetime
from picamera import PiCamera
from time import sleep
from os.path import join


def main(prefix: str = "pic_", rotation: int = 0, out: str = ".", warmup: int = 3):

    date = datetime.now().strftime("%y%m%d_%H%M%S")
    fname = f"{prefix}{date}.jpg"
    fpath = join(out, fname)
    with PiCamera() as camera:
        camera.rotation = rotation
        # Take picture
        print(f"Warming up ({warmup} sec)")
        camera.start_preview()
        sleep(warmup)
        camera.capture(fpath)
        print(f"Picture saved in {fpath}")
        camera.stop_preview()


if __name__ == "__main__":
    typer.run(main)
