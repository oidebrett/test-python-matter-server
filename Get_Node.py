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
        "message_id": "2",
        "command": "get_node",
        "args": {
            "node_id": 1
        }
    }

    asyncio.run(produce(message=json.dumps(messageObject), host='ws://192.168.1.45', port=5580))