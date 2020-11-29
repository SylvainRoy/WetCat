#!/usr/bin/env python3

"""
Small script to check all system dependencies are ready before to launch the main script.
To be used from a service script.
"""

import time
import os


# Waiting for the NFS drive on maison to be ready
while True:
    try:
        with open("/mnt/maison/log.txt", mode="a") as log:
            print("NFS checked ok", file=log)
        break
    except OSError as err:
        time.sleep(1)

# Starting main script
os.system("nohup /usr/bin/python3 /home/pi/dev/WetCat/tools/collector.py --out /mnt/maison/ &")
