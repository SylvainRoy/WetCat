#!/usr/bin/env python3

"""
Takes a picture.
"""

import sys

from datetime import datetime
from picamera import PiCamera
from time import sleep

picfile = "picture" + datetime.now().strftime("%y%m%d_%H%M%S") + ".jpg"
if len(sys.argv) > 0:
    picfile = sys.argv[0]

camera = PiCamera()
camera.rotation = 180

# Take picture
camera.start_preview()
sleep(5)
camera.capture(picfile)
camera.stop_preview()

print(f"Picture saved in {picfile}")
