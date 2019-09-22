#!/usr/bin/env python

from aiohttp import web, ClientSession

async def handle(request):
    async with ClientSession() as session:
        response = await session.get('http://0.0.0.0:8080/')
        text = await response.text()
        text = "He said: " + text
        return web.Response(text=text)

app = web.Application()
app.add_routes([web.get('/', handle)])

web.run_app(app=app, port=8081)
