#!/usr/bin/python3


# Python imports
import argparse, faulthandler, traceback
from setproctitle import setproctitle

import tracemalloc
tracemalloc.start()


# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from __init__ import Main


if __name__ == "__main__":
    try:
        setproctitle('solarfm')
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--new-tab", "-t", default="", help="Open a file into new tab.")
        parser.add_argument("--new-window", "-w", default="", help="Open a file into a new window.")

        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        Main(args, unknownargs)
        Gtk.main()
    except Exception as e:
        print(repr(e))
        event_system.keep_ipc_alive = False
        if debug:
            traceback.print_exc()
