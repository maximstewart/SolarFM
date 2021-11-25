#!/usr/bin/python3


# Python imports
import argparse
from setproctitle import setproctitle

import tracemalloc
tracemalloc.start()


# Gtk imports
import gi, faulthandler, traceback
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from __init__ import Main


if __name__ == "__main__":
    try:
        setproctitle('PyFM')
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--new-tab", "-t", help="Open a file into new tab.")
        parser.add_argument("--new-window", "-w", help="Open a file into a new window.")

        # Read arguments (If any...)
        args = parser.parse_args()
        Main(args)
        Gtk.main()
    except Exception as e:
        event_system.keep_ipc_alive = False
        if debug:
            traceback.print_exc()
