import builtins

class Builtins:
    # Makeshift "events" type system FIFO
    def push_gui_event(event):
        gui_events.append(event)

    def push_fm_event(event):
        fm_events.append(event)

    def pop_gui_event():
        gui_events.pop(0)

    def pop_fm_event():
        fm_events.pop(0)

    def read_gui_event():
        return gui_events[0]

    def read_fm_event():
        return fm_events[0]


    builtins.gui_events = []
    builtins.fm_events  = []

    # NOTE: Just reminding myself we can add to builtins two different ways...
    __builtins__.update({"push_gui_event": push_gui_event})
    __builtins__.update({"push_fm_event": push_fm_event})

    builtins.pop_gui_event  = pop_gui_event
    builtins.pop_fm_event   = pop_fm_event
    builtins.read_gui_event = read_gui_event
    builtins.read_fm_event  = read_fm_event
