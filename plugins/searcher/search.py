#!/usr/bin/python3


# Python imports
import os, traceback, argparse, time, json, base64
from setproctitle import setproctitle

# Lib imports

# Application imports



_files_fifo_file  = f"/tmp/search_files_fifo"
_grep_fifo_file   = f"/tmp/grep_files_fifo"

filter = (".mkv", ".mp4", ".webm", ".avi", ".mov", ".m4v", ".mpg", ".mpeg", ".wmv", ".flv") + \
            (".png", ".jpg", ".jpeg", ".gif", ".ico", ".tga", ".webp") + \
            (".psf", ".mp3", ".ogg", ".flac", ".m4a")

file_result_set = []


def file_search(fifo, path, query):
    try:
        for file in os.listdir(path):
            target = os.path.join(path, file)
            if os.path.isdir(target):
                file_search(fifo, target, query)
            else:
                if query.lower() in file.lower():
                    # file_result_set.append([target, file])
                    data = json.dumps([target, file])
                    fifo.write(data)
                    time.sleep(0.01)
    except Exception as e:
        print("Couldn't traverse to path. Might be permissions related...")
        traceback.print_exc()

def _search_for_string(file, query):
    try:
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

            # NOTE: Push to fifo here after loop
        with open(_grep_fifo_file, 'w') as fifo:
            data = json.dumps(grep_result_set)
            fifo.write(data)
            time.sleep(0.05)
    except Exception as e:
        print("Couldn't read file. Might be binary or other cause...")
        traceback.print_exc()


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
       with open(_files_fifo_file, 'w') as fifo:
           file_search(fifo, args.dir, args.query)

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
