#!/usr/bin/env python3

"""
Records a 15 seconds video.
"""

import sys

from datetime import datetime
from picamera import PiCamera
from time import sleep

date = datetime.now().strftime("%y%m%d_%H%M%S")
movfile = f"video_{date}.h264"
if len(sys.argv) > 1:
    movfile = sys.argv[1]

camera = PiCamera()
camera.rotation = 180

camera.start_preview()
camera.start_recording(movfile)
sleep(15)
camera.stop_recording()
camera.stop_preview()

print(f"Video saved in {movfile}")
