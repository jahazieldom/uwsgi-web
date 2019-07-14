#!/usr/bin/env python

import configparser
import asyncio
import websockets
import logging
import time
import socket
import json
import subprocess
import argparse
import functools
from websockets import exceptions

USERS = set()

def get_json_data(stats_sock):
    """Returns uwsgi stats data as dict from the socket file."""
    data_dict = {}
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(stats_sock)
            while True:
                data = s.recv(4096)
                if len(data) < 1:
                    break
                data_dict += data.decode("utf8", "ignore")
            s.close()
        data_dict = json.loads(data_dict)
    except Exception as e:
        pass
    return data_dict

def state_event(stats=[]):
    """Returns the data of all stats sockets."""
    sockets = []
    for s in set(stats):
        data = get_json_data(s)
        data["socket_file"] = s
        sockets.append(data)
    return json.dumps(sockets)

def kill_pid(pid):
    """Kill process by id."""
    logging.info("Killing PID {}".format(pid))
    subprocess.call("kill -9 {}".format(pid), shell=True)

async def notify_state(stats=[]):
    """Sends uwsgi data to all USERS set"""
    if USERS:  
        message = state_event(stats=stats)
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    """Add the websocket connection to the USERS set"""
    logging.info("Register socket {}".format(websocket))
    USERS.add(websocket)

async def unregister(websocket):
    """Removes the websocket connection to the USERS set"""
    logging.info("Unregister socket {}".format(websocket))
    USERS.remove(websocket)

async def command(websocket, path, *, stats=[]):
    """Command server"""
    logging.info("Stats sockets files {}".format(stats))
    await register(websocket)
    try:
        while True:
            await websocket.send(state_event(stats=stats))
            async for message in websocket:
                data = json.loads(message)
                if data["action"] == "data":
                    await notify_state(stats=stats)
                elif data["action"] == "kill":
                    kill_pid(data["pid"])
                    await notify_state(stats=stats)
                else:
                    logging.error("unsupported event {}", data)
            time.sleep(0.5)
    except exceptions.ConnectionClosedOK as e:
        pass
    finally:
        await unregister(websocket)

def set_args():
    """Create the cli args parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stats",
        action="append",
        help="Path to uwsgi stats socket file",
        nargs="?",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Socket server host"
    )
    parser.add_argument(
        "--port",
        type=str,
        default="6789",
        help="Socket server port"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Log level"
    )
    parser.add_argument(
        "--log-format",
        type=str,
        default="%(levelname)s:%(asctime)s:%(message)s",
        help=(
            "Log format (https://docs.python.org"
            "/2/library/logging.html#logrecord-attributes)"
        )
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s - Version 1.0"
    )

    return parser.parse_args()

def set_log_config(config):
    """Sets logging module configuration"""
    level = config.get("level")
    log_format = config.get("format")
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt="%d/%m/%Y %H:%M:%S"
    )

if __name__ == "__main__":
    args = set_args()
    host = args.host
    port = args.port
    log_level = args.log_level
    log_format = args.log_format

    set_log_config({
        "level": log_level,
        "format": log_format
    })

    if args.stats:
        stats = set(args.stats)
        start_server = websockets.serve(
            functools.partial(command, stats=stats), host, port
        )
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    else:
        logging.error("No socket file specified")
