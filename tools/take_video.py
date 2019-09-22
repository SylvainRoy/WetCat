#!/usr/bin/env python3

"""
Records a 15 seconds video.
"""

import sys

from datetime import datetime
from picamera import PiCamera
from time import sleep

movfile = "video" + datetime.now().strftime("%y%m%d_%H%M%S") + ".h264"
if len(sys.argv) > 0:
    movfile = sys.argv[0]

camera = PiCamera()
camera.rotation = 180

camera.start_preview()
camera.start_recording(movfile)
sleep(15)
camera.stop_recording()
camera.stop_preview()

print(f"Video saved in {movfile}")
