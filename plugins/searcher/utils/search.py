#!/usr/bin/python3


# Python imports
import os
import traceback
import argparse
import subprocess
import json
import base64
import time
from datetime import datetime
from setproctitle import setproctitle
from multiprocessing.connection import Client

# Lib imports

# Application imports




_ipc_address = f'/tmp/solarfm-search_grep-ipc.sock'
_ipc_authkey = b'' + bytes(f'solarfm-search_grep-ipc', 'utf-8')

filter = (".cpp", ".css", ".c", ".go", ".html", ".htm", ".java", ".js", ".json", ".lua", ".md", ".py", ".rs", ".toml", ".xml", ".pom") + \
            (".txt", ".text", ".sh", ".cfg", ".conf", ".log")

# NOTE: Create timestamp of when this launched. Is used in IPC to see if
# we are stale and that new call didn't fully kill this or older processes.
dt = datetime.now()
ts = datetime.timestamp(dt)


def _log(message: str = "No message passed in...") -> None:
    print(message)


def send_ipc_message(message) -> None:
    conn = Client(address = _ipc_address, family = "AF_UNIX", authkey = _ipc_authkey)
    conn.send(message)
    conn.close()

    # NOTE: Kinda important as this prevents overloading the UI thread
    time.sleep(0.05)


def file_search(path: str = None, query: str = None) -> None:
    if not path or not query: return

    try:
        for _path, _dir, _files in os.walk(path, topdown = True, onerror = _log, followlinks = True):
             for file in _files:
                 if query in file.lower():
                     target = os.path.join(_path, file)
                     data = f"SEARCH|{ts}|{json.dumps([target, file])}"
                     send_ipc_message(data)
    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()


def grep_search(target: str = None, query: str = None):
    if not target or not query: return

    # NOTE: -n = provide line numbers, -R = Search recursive in given target
    #       -i = insensitive, -F = don't do regex parsing. (Treat as raw string)
    command    = ["grep", "-n", "-R", "-i", "-F", query, target]
    proc       = subprocess.Popen(command, stdout = subprocess.PIPE, encoding = "utf-8")
    raw_data   = proc.communicate()[0].strip()
    proc_data  = raw_data.split("\n")   # NOTE: Will return data AFTER completion (if any)
    collection = {}

    for line in proc_data:
        try:
            parts    = line.split(":", 2)
            if not len(parts) == 3:
                continue

            file, line_no, data = parts
            b64_file = base64.urlsafe_b64encode(file.encode('utf-8')).decode('utf-8')
            b64_data = base64.urlsafe_b64encode(data.encode('utf-8')).decode('utf-8')

            if b64_file in collection.keys():
                collection[f"{b64_file}"][f"{line_no}"] = b64_data
            else:
                collection[f"{b64_file}"] = {}
                collection[f"{b64_file}"] = { f"{line_no}": b64_data}

        except Exception as e:
            traceback.print_exc()

    proc.terminate()
    data = f"GREP|{ts}|{json.dumps(collection, separators=(',', ':'), indent=4)}"
    send_ipc_message(data)
    collection = {}


def search(args):
    path = args.dir
    if (path[0] == "'" and path[-1] == "'") or \
        path[0] == '"' and path[-1] == '"':
            path = path[1:-1]

    if args.type == "file_search":
        file_search(path, args.query.lower())

    if args.type == "grep_search":
        grep_search(path, args.query.encode("utf-8"))


if __name__ == "__main__":
    try:
        setproctitle('SolarFM: File Search - Grepy')

        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--type", "-t", default=None, help="Type of search to do.")
        parser.add_argument("--dir", "-d", default=None, help="Directory root for search type.")
        parser.add_argument("--query", "-q", default=None, help="Query search is working against.")

        # Read arguments (If any...)
        args = parser.parse_args()
        search(args)

        data = f"SEARCH_DONE|{ts}|0"
        send_ipc_message(data)
    except Exception as e:
        traceback.print_exc()

        data = f"SEARCH_DONE|{ts}|1"
        send_ipc_message(data)
