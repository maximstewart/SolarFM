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

    def unsubscribe(self, event_type, fn):
        self.subscribers[event_type].remove(fn)

    def unsubscribe_all(self, event_type):
        self.subscribers.pop(event_type, None)

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

    def emit_and_await(self, event_type, data = None):
        """ NOTE: Should be used when signal has only one listener and vis-a-vis """
        if event_type in self.subscribers:
            response = None
            for fn in self.subscribers[event_type]:
                if data:
                    if hasattr(data, '__iter__') and not type(data) is str:
                        response = fn(*data)
                    else:
                        response = fn(data)
                else:
                    response = fn()

                if not response in (None, ''):
                    break

            return response
