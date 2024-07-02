import asyncio
import aiohttp
from aiohttp import web
import json
from concurrent.futures import ThreadPoolExecutor

HOST='192.168.1.45' 
PORT=5580
URL = f'http://{HOST}:{PORT}/ws'

# create the shared queue for sharing inbound messages between webserver and websocket queues
queue = asyncio.Queue()

routes = web.RouteTableDef()


@routes.get('/')
async def handler(request):
    return web.Response(text="Async REST API in Python3")

@routes.get('/command')
async def return_command(request):
    json_str = request.rel_url.query.get('json', '')

    messageObject = json.loads(json_str)

    # add to the queue
    await queue.put(json_str)

    return web.Response(text=f'The request data was {json_str}')

@routes.get('/nodes')
async def return_nodes(request):
    messageObject = {
            "message_id": "5",
            "command": "get_nodes"
        }

    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:

        await ws.send_json(messageObject)

        async for msg in ws:
            print('Message received from server:', json.dumps(msg.json()))

            if msg.type in (aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY):
                message_respone = json.loads(msg.data)
                #We are looking for the result
                if "result" in message_respone:
                    print("Result:", message_respone["result"])
                    print(message_respone["result"])
                    break

            if msg.type in (aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR):
                break

    return web.Response(text=f'{message_respone["result"]}')

async def run(ws):
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print('Message received from server:', json.dumps(msg.json()))

async def ainput(prompt: str = ''):
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()
    
async def prompt(ws):
    while True:
        msg = await ainput('> ')
        await ws.send_str(msg)

async def consumer(ws, queue):
    print('Consumer: Running')

    # consume work
    while True:
        # get a unit of work
        item = await queue.get()
        # check for stop signal
        if item is None:
            break
        # report
        await ws.send_str(item)
    # all done
    print('Consumer: Done')


async def initialization():
    app = web.Application()
    app.add_routes(routes)

    return app

async def main():

    # set up the REST server
    app = await initialization()
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner)    
    await site.start()


    # add the websocket client handler to the loop
    async with aiohttp.ClientSession().ws_connect(URL) as ws:
        run_task = asyncio.create_task(run(ws))
#        prompt_task = asyncio.create_task(prompt(ws))
        poll_task = asyncio.create_task(consumer(ws, queue))

        await asyncio.gather(poll_task, run_task)

    # wait forever
    await asyncio.Event().wait()



if __name__ == '__main__':
    print('Type "exit" to quit')
    asyncio.run(main())
