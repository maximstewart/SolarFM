#!/usr/bin/python3


# Python imports
import os, traceback, argparse, json, base64
from setproctitle import setproctitle
from multiprocessing.connection import Client

# Lib imports

# Application imports




_ipc_address = f'/tmp/solarfm-search_grep-ipc.sock'
_ipc_authkey = b'' + bytes(f'solarfm-search_grep-ipc', 'utf-8')

filter = (".mkv", ".mp4", ".webm", ".avi", ".mov", ".m4v", ".mpg", ".mpeg", ".wmv", ".flv") + \
            (".png", ".jpg", ".jpeg", ".gif", ".ico", ".tga", ".webp") + \
            (".psf", ".mp3", ".ogg", ".flac", ".m4a")

file_result_set = []


def send_ipc_message(message) -> None:
    try:
        conn = Client(address=_ipc_address, family="AF_UNIX", authkey=_ipc_authkey)

        conn.send(message)
        conn.close()
    except ConnectionRefusedError as e:
        print("Connection refused...")
    except Exception as e:
        print(repr(e))


def file_search(path, query):
    try:
        for file in os.listdir(path):
            target = os.path.join(path, file)
            if os.path.isdir(target):
                file_search(target, query)
            else:
                if query.lower() in file.lower():
                    data = f"SEARCH|{json.dumps([target, file])}"
                    send_ipc_message(data)
    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()

def _search_for_string(file, query):
    b64_file = base64.urlsafe_b64encode(file.encode('utf-8')).decode('utf-8')
    grep_result_set = {}

    with open(file, 'r') as fp:
        for i, line in enumerate(fp):
            if query in line:
                b64_line = base64.urlsafe_b64encode(line.encode('utf-8')).decode('utf-8')

                if f"{b64_file}" in grep_result_set.keys():
                    grep_result_set[f"{b64_file}"][f"{i+1}"] = b64_line
                else:
                    grep_result_set[f"{b64_file}"] = {}
                    grep_result_set[f"{b64_file}"] = {f"{i+1}": b64_line}

        data = f"GREP|{json.dumps(grep_result_set)}"
        send_ipc_message(data)


def grep_search(path, query):
    try:
        for file in os.listdir(path):
            target = os.path.join(path, file)
            if os.path.isdir(target):
                grep_search(target, query)
            else:
                if not target.lower().endswith(filter):
                        _search_for_string(target, query)
    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()

def search(args):
    if args.type == "file_search":
        file_search(args.dir, args.query)

    if args.type == "grep_search":
        grep_search(args.dir, args.query)


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
