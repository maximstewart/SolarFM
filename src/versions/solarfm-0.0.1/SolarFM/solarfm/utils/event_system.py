# Python imports
from collections import defaultdict

# Lib imports

# Application imports




class EventSystem:
    """ Create event system. """

    def __init__(self):
        self.subscribers = defaultdict(list)


    def subscribe(self, event_type, fn):
        self.subscribers[event_type].append(fn)

    def emit(self, event_type, data = None):
        if event_type in self.subscribers:
            for fn in self.subscribers[event_type]:
                if data:
                    if hasattr(data, '__iter__') and not type(data) is str:
                        fn(*data)
                    else:
                        fn(data)
                else:
                    fn()
