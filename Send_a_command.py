import asyncio
import websockets
import json
import sys
import os
from pathlib import Path

# Import the CHIP clusters
from chip.clusters import Objects as clusters

path = "../python-matter-server"
sys.path.append(os.path.abspath(path))

# Import the ability to turn objects into dictionaries, and vice-versa
from matter_server.common.helpers.util import dataclass_from_dict,dataclass_to_dict

async def produce(host: str, port: int):
    print(host)
    print(port)
    url = f"{host}:{port}/ws"

    command = clusters.OnOff.Commands.On()
    payload = dataclass_to_dict(command)

    message = {
        "message_id": "device_command",
        "command": "device_command",
        "args": {
            "endpoint_id":  1,
            "node_id":  1,
            "payload": payload,
            "cluster_id": command.cluster_id,
            "command_name": "Toggle"
        }
    }

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps(message))
        await ws.recv()


if __name__ == "__main__":

    asyncio.run(produce(host='ws://127.0.0.1', port=5580))