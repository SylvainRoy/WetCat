#!/usr/bin/env python

import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://0.0.0.0:8081')
        print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
