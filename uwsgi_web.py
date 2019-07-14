#!/usr/bin/env python

import cherrypy
import subprocess
import argparse
from os.path import abspath

CP_CONF = {
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': abspath('./dist') # staticdir needs an absolute path
    }
}

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

class HttpServer(object):
    @cherrypy.expose
    def index(self):
        return open("dist/index.html")

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8000})
    cherrypy.tree.mount(HttpServer(), "/", CP_CONF)
    cherrypy.engine.start()

    args = set_args()
    host = args.host
    port = args.port
    log_level = args.log_level
    log_format = args.log_format
    
    cmd = [
    	"python",
    	"websocket_server.py",
    ]

    if args.stats:
    	cmd += ["--stats=" + x for x in args.stats]

    if log_level:
    	cmd += ["--log-level", log_level]

    if log_format:
    	cmd += ["--log-format", log_format]

    if host:
    	cmd += ["--host", host]

    if port:
    	cmd += ["--port", port]

    subprocess.call(cmd)

