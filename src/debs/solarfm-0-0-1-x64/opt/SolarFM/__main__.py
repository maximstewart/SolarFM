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
from app import Application


if __name__ == "__main__":
    """ Set process title, get arguments, and create GTK main thread. """

    try:
        # import web_pdb
        # web_pdb.set_trace()

        setproctitle('SolarFM')
        faulthandler.enable()  # For better debug info
        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--new-tab", "-t", default="", help="Open a file into new tab.")
        parser.add_argument("--new-window", "-w", default="", help="Open a file into a new window.")

        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        Application(args, unknownargs)
        Gtk.main()
    except Exception as e:
        traceback.print_exc()
        quit()
