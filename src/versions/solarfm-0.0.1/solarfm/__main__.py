#!/usr/bin/python3

# Python imports
import argparse
import faulthandler
import locale
import traceback
from setproctitle import setproctitle

# Lib imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Application imports
from __builtins__ import *
from app import Application




def run():
    try:
        locale.setlocale(locale.LC_NUMERIC, 'C')

        setproctitle(f"{app_name}")
        faulthandler.enable()  # For better debug info

        parser = argparse.ArgumentParser()
        # Add long and short arguments
        parser.add_argument("--debug", "-d", default="false", help="Do extra console messaging.")
        parser.add_argument("--trace-debug", "-td", default="false", help="Disable saves, ignore IPC lock, do extra console messaging.")
        parser.add_argument("--no-plugins", "-np", default="false", help="Do not load plugins.")

        parser.add_argument("--new-tab", "-t", default="", help="Open a file into new tab.")
        parser.add_argument("--new-window", "-w", default="", help="Open a file into a new window.")

        # Read arguments (If any...)
        args, unknownargs = parser.parse_known_args()

        if args.debug == "true":
            settings.set_debug(True)

        if args.trace_debug == "true":
            settings.set_trace_debug(True)

        settings.do_dirty_start_check()
        Application(args, unknownargs)
        Gtk.main()
    except Exception as e:
        traceback.print_exc()
        quit()


if __name__ == "__main__":
    """ Set process title, get arguments, and create GTK main thread. """
    run()
