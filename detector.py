#!/usr/bin/env python3

import time
import asyncio
import random
import logging
import json
from datetime import datetime, timedelta
from concurrent.futures.thread import ThreadPoolExecutor
from aiohttp import web, WSMsgType


#
# Config
#

PERIOD = 3   # Delay between two measures.
SPIKE = 8    # Duration of a spike of water.


#
# Control of the switches
#

class Switch:
    """
    Controler of the state of a switch.
    """

    def __init__(self, name):
        self.name = name
        self.state = False
        self.detection = True
        self.timeoff = None

    async def set(self, state=None, detection=None, duration=None):
        """
        Set the state of the switch.
        """
        previous_state = self.state
        if state is not None:
            self.state = state
        if detection is not None:
            self.detection = detection
        if not(self.state):
            self.timeoff = None
        elif duration is not None:
            self.timeoff = datetime.now() + timedelta(seconds=duration)
        # Activate the switch if needed
        if not(previous_state) and self.state:
            await self._activate()
        # Publish new state
        await self.publish_state()

    async def burst(self):
        """
        Activate the switch for a short period of time.
        Detection must be "on'.
        """
        logging.debug(f"Burst requested on {self.name} [state:{self.state} detection:{self.detection}]")
        if not(self.state) and self.detection:
            await self.set(state=True, duration=SPIKE)

    async def _activate(self):
        """
        Activate the remote switch.
        Do not use directly: self.set() ensure consistency between the state of the
        object and the remote switch.
        """
        # todo: remotely activate the switch
        logging.debug(f"Switch {self.name} turned on until {self.timeoff}.")

    async def _deactivate(self):
        """
        Deactivate the remote switch.
        Do not use directly: self.set() ensure consistency between the state of the
        object and the remote switch.
        """
        # todo: remotely deactivate the switch
        logging.debug(f"Switch {self.name} turned off.")

    async def watchman(self):
        """
        Callback to continuously monitor the state of the switch and turn it off when needed.
        """
        logging.debug(f"Switch {self.name}: starting watchman.")
        while True:
            if self.state:
                if (self.timeoff is None) or (self.timeoff <= datetime.now()):
                    logging.debug(f"Switch {self.name}: time to stop.")
                    await self._deactivate()
                    self.timeoff = None
                    self.state = False
                await self.publish_state()
            await asyncio.sleep(1)

    def duration(self):
        """Return the duration in second until switch is turn off."""
        if self.timeoff is None:
            return 0
        delta = self.timeoff - datetime.now()
        return delta.seconds

    def to_dict(self):
        """Return the state of the switch in a dict."""
        return {"switch": self.name,
                "state": self.state,
                "detection": self.detection,
                "duration": self.duration()}

    async def publish_state(self):
        """Publish the state of the switch to all web sockets."""
        for ws in Websockets:
            logging.debug("Websocket send: {}".format(self.to_dict()))
            await ws.send_json(self.to_dict())



Switches = {
    "west": Switch("west"),
    "south": Switch("south")
}


#
# Web app
#

async def get_app(request):
#    with open("./static/index.html") as f:
#        content = f.read()
    return web.FileResponse(path="./static/index.html")


async def get_switch(request):
    """
    Get the state of a switch.

    curl -X GET http://localhost:8080/switch/
    curl -X GET http://localhost:8080/switch/west
    """
    switch_name = request.match_info.get('switch', None)
    if switch_name is None:
        return web.json_response({"status": "ok",
                                  "switches": list(Switches.keys())})
    if switch_name not in Switches.keys():
        return web.json_response({"status": "error",
                                  "message": "Switch name must be in {}.".format(list(Switches.keys()))})
    switch = Switches[switch_name]
    return web.json_response({"status": "ok",
                              "state": switch.state,
                              "detection": switch.detection,
                              "duration": switch.duration()})


async def put_switch(request):
    """
    Set the state of a switch.

    curl -X PUT http://localhost:8080/switch/west -d '{"state":true, "detection":false, "duration":30}'
    """
    # Check parameters
    switch_name = request.match_info.get('switch', None)
    json = await request.json()
    state = json.get("state", None)
    detection = json.get("detection", None)
    duration = json.get("duration", 0)
    if switch_name is None:
        return web.json_response({"status": "error",
                                  "message": "Missing switch name."})
    if switch_name not in Switches.keys():
        return web.json_response({"status": "error",
                                  "message": "Switch name must be in {}".format(list(Switches.keys()))})
    if state not in [True, False, None]:
        return web.json_response({"status": "error",
                                  "message": "Switch state must a boolean."})
    if detection not in [True, False, None]:
        return web.json_response({"status": "error",
                                  "message": "Switch detection must be a boolean."})
    if duration is not None:
        if not (0 <= duration <= 600):
            return web.json_response({"status": "error",
                                      "message": "Duration cannot exceed 600 seconds."})

    # Register changes and initiate action
    asyncio.create_task(
        Switches[switch_name].set(state=state,
                                  detection=detection,
                                  duration=duration))

    # Reply
    switch = Switches[switch_name]
    return web.json_response({"status": "ok"})


Websockets = set()

async def websocket_handler(request):
    global Websockets

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    Websockets.add(ws)

    async for msg in ws:
        logging.debug(f"Websocket event: {msg.type}")

        if msg.type == WSMsgType.TEXT:
            logging.debug(f"Websocket received: {msg.data}")
            message = json.loads(msg.data)
            switch = message["switch"]
            action = message["action"]

            if action == "status":
                await Switches[switch].publish_state()

            elif action == "change":
                # Reformat parameters
                param = {}
                param["duration"] = message.get("duration", None)
                param["state"] = message.get("state", None)
                param["detection"] = message.get("detection", None)
                # Change the state of the switch
                await Switches[switch].set(**param)

            else:
                logging.error("Websocket unhandled action! {}".format(msg.type))

        elif msg.type == WSMsgType.ERROR:
            logging.debug("Websocket closed with exception {}".format(ws.exception()))
            break

        else:
            logging.error("Websocket unhandled event! {}".format(msg.type))

        logging.debug("Websocket end of handling of event: {}".format(msg.type))


    logging.debug("Websocket closed {}.".format(msg.type))
    Websockets.remove(ws)
    return ws


app = web.Application()
app.add_routes([web.get('/', get_app),
                web.get('/switch/', get_switch),
                web.get('/switch/{switch}', get_switch),
                web.put('/switch/{switch}', put_switch),
                web.get('/ws', websocket_handler),
                web.static('/', './static')
])


#
# Cat detection
#

def detection():
    """
    Returns the region in which a cat is detected.
    """
    # todo: make this the real thing!
    # Simulate a lengthy processing and a possible cat detection.
    time.sleep(3)
    regions = ["west", "south", None]
    region = regions[random.randint(0, 2)]
    return region


async def detection_manager():
    """
    Infinite loop to manage the cat detection system.
    """
    logging.debug("Starting detection loop!")
    while True:
        switch = await loop.run_in_executor(None, detection)
        logging.debug(f"Cat detection: {switch}")
        if switch is not None:
            await Switches[switch].burst()
        await asyncio.sleep(PERIOD)


#
# Start cat detection and web app.
#

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s) %(message)s')

loop = asyncio.get_event_loop()
EXECUTOR = ThreadPoolExecutor(1)
loop.set_default_executor(EXECUTOR)

# Set up a backgroup task to detect cats.
loop.create_task(detection_manager())

# Set up background tasks to turn off the switches.
for switch_name, switch in Switches.items():
    loop.create_task(switch.watchman())

# Run the web server and the various background tasks.
web.run_app(app)
