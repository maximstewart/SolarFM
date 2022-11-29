#!/usr/bin/python3


# Python imports
import os
import traceback
import argparse
import threading
import json
import base64
import time
import pickle
from setproctitle import setproctitle
from multiprocessing.connection import Client

# Lib imports

# Application imports




_ipc_address = f'/tmp/solarfm-search_grep-ipc.sock'
_ipc_authkey = b'' + bytes(f'solarfm-search_grep-ipc', 'utf-8')

filter = (".cpp", ".css", ".c", ".go", ".html", ".htm", ".java", ".js", ".json", ".lua", ".md", ".py", ".rs", ".toml", ".xml", ".pom") + \
            (".txt", ".text", ".sh", ".cfg", ".conf", ".log")


# NOTE: Threads WILL NOT die with parent's destruction.
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=False).start()
    return wrapper

# NOTE: Threads WILL die with parent's destruction.
def daemon_threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper


def send_ipc_message(message) -> None:
    conn = Client(address=_ipc_address, family="AF_UNIX", authkey=_ipc_authkey)
    conn.send(message)
    conn.close()

    # NOTE: Kinda important as this prevents overloading the UI thread
    time.sleep(0.05)


def file_search(path, query):
    try:
        for _path, _dir, _files in os.walk(path, topdown = True):
             for file in _files:
                 if query in file.lower():
                     target = os.path.join(_path, file)
                     data = f"SEARCH|{json.dumps([target, file])}"
                     send_ipc_message(data)
    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()

def _search_for_string(file, query):
    b64_file = base64.urlsafe_b64encode(file.encode('utf-8')).decode('utf-8')
    grep_result_set = {}
    padding = 15

    with open(file, 'rb') as fp:
        # NOTE: I know there's an issue if there's a very large file with content
        #       all on one line will lower and dupe it. And, yes, it will only
        #       return one instance from the file.
        try:
            for i, raw in enumerate(fp):
                line   = None
                llower = raw.lower()
                if not query in llower:
                    continue

                if len(raw) > 72:
                    start  = 0
                    end    = len(raw) - 1
                    index  = llower.index(query)
                    sindex = llower.index(query) - 15 if index >= 15 else abs(start - index) - index
                    eindex = sindex + 15 if end > (index + 15) else abs(index - end) + index
                    line   = raw[sindex:eindex]
                else:
                    line = raw

                b64_line = base64.urlsafe_b64encode(line).decode('utf-8')
                if f"{b64_file}" in grep_result_set.keys():
                    grep_result_set[f"{b64_file}"][f"{i+1}"] = b64_line
                else:
                    grep_result_set[f"{b64_file}"] = {}
                    grep_result_set[f"{b64_file}"] = {f"{i+1}": b64_line}

        except Exception as e:
            ...

        try:
            data = f"GREP|{json.dumps(grep_result_set)}"
            send_ipc_message(data)
        except Exception as e:
            ...



@daemon_threaded
def _search_for_string_threaded(file, query):
    _search_for_string(file, query)

def grep_search(path, query):
    try:
        for file in os.listdir(path):
            target = os.path.join(path, file)
            if os.path.isdir(target):
                grep_search(target, query)
            else:
                if target.lower().endswith(filter):
                    size = os.path.getsize(target)
                    if not size > 5000:
                        _search_for_string(target, query)
                    else:
                        _search_for_string_threaded(target, query)

    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()

def search(args):
    if args.type == "file_search":
        file_search(args.dir, args.query.lower())

    if args.type == "grep_search":
        grep_search(args.dir, args.query.lower().encode("utf-8"))


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
    except Exception as e:
        traceback.print_exc()
