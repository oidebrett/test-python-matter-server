import asyncio
import websockets
import json

async def produce(message: str, host: str, port: int):
    print(message)
    print(host)
    print(port)
    url = f"{host}:{port}/ws"
    async with websockets.connect(url) as ws:
        await ws.send(message)
        response = await ws.recv()
        print(response)


if __name__ == "__main__":
   
    messageObject = {
        "message_id": "3",
        "command": "start_listening"
    }

    asyncio.run(produce(message=json.dumps(messageObject), host='ws://127.0.0.1', port=5580))