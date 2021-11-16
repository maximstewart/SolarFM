#!/usr/bin/python3


# Python imports
import argparse
from setproctitle import setproctitle

import tracemalloc
tracemalloc.start()


# Gtk imports
import gi, faulthandler, traceback
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

# Application imports
from __init__ import Main


if __name__ == "__main__":
    try:
        setproctitle('PyFM')
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--file", "-f", default="default", help="JUST SOME FILE ARG.")

        # Read arguments (If any...)
        args = parser.parse_args()
        main = Main(args)
        gtk.main()
    except Exception as e:
        traceback.print_exc()
