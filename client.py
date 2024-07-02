import asyncio
import os
import json

import aiohttp
from aiorun import run

import sys
import os
from pathlib import Path

# Import the CHIP clusters
from chip.clusters import Objects as clusters
from chip.clusters.ClusterObjects import (
    ALL_ATTRIBUTES,
    ALL_CLUSTERS,
    Cluster,
    ClusterAttributeDescriptor,
)

path = "../python-matter-server"
sys.path.append(os.path.abspath(path))

# Import the ability to turn objects into dictionaries, and vice-versa
from matter_server.common.helpers.util import dataclass_from_dict,dataclass_to_dict, create_attribute_path, create_attribute_path_from_attribute

HOST='127.0.0.1' 
PORT=5580
URL = f'http://{HOST}:{PORT}/ws'

async def main1():
    command = clusters.OnOff.Commands.Toggle()
    print(command.cluster_id)
    payload=dataclass_to_dict(command)
    command_name = command.__class__.__name__

    print("payload")
    print(payload)

async def run_matter():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:

        await prompt_and_send(ws)
        async for msg in ws:
            print('Message received from server:', json.dumps(msg.json()))
            await prompt_and_send(ws)

            if msg.type in (aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR):
                break




async def prompt_and_send(ws):
    new_msg_to_send = input('Type a message to send to the server: ')
    if new_msg_to_send == 'exit':
        print('Exiting!')
        raise SystemExit(0)
    
    elif new_msg_to_send == 'commission_on_network':
        messageObject = {
            "message_id": "1",
            "command": "commission_on_network",
            "args": {
                "setup_pin_code": 20202021
            }
        }
    elif new_msg_to_send == 'device_command':
        command = clusters.OnOff.Commands.Toggle()
        payload = dataclass_to_dict(command)
        command_name = command.__class__.__name__

        messageObject = {
            "message_id": "2",
            "command": "device_command",
            "args": {
                "endpoint_id":  2,
                "node_id":  1,
                "cluster_id": command.cluster_id,
                "command_name": command_name,
                "payload": payload
            }
        } 
    elif new_msg_to_send == 'write_attribute':
        attribute_path = create_attribute_path_from_attribute(0, clusters.BasicInformation.Attributes.Location)

        messageObject = {
            "message_id": "4",
            "command": "write_attribute",
            "args": {
                "endpoint_id":  0,
                "node_id":  1,
                "attribute_path": attribute_path,
                "value": "IE"
            }

        }
    elif new_msg_to_send == 'get_nodes':
        messageObject = {
            "message_id": "5",
            "command": "get_nodes"
        }
    elif new_msg_to_send == 'start_listening':
        messageObject = {
            "message_id": "6",
            "command": "start_listening"
        }

    else:
        messageObject = {
            "message_id": "7",
            "command" : "test"
        }

    await ws.send_json(messageObject)


async def handle_stop(loop: asyncio.AbstractEventLoop):
    """Handle server stop."""
    #await server.stop()
    return



if __name__ == '__main__':
    print('Type "exit" to quit')
    # run the server
    run(run_matter(), shutdown_callback=handle_stop)

