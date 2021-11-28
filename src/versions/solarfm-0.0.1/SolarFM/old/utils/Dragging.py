import os, gi

gi.require_version('Gdk', '3.0')

from gi.repository import Gdk
from gi.repository import GObject


class Dragging:
    def __init__(self):
        # higher values make movement more performant
        # lower values make movement smoother
        self.SENSITIVITY = 1
        self.desktop     = None
        self.EvMask      = Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK
        self.offsetx     = 0
        self.offsety     = 0
        self.px          = 0
        self.py          = 0
        self.maxx        = 0
        self.maxy        = 0

    def connectEvents(self, desktop, widget):
        self.desktop = desktop
        widget.set_events(self.EvMask)
        widget.connect("button_press_event", self.press_event)
        widget.connect("motion_notify_event", self.draggingEvent)
        widget.show()

    def press_event(self, w, event):
        if event.button == 1:
            p = w.get_parent()
            # offset == distance of parent widget from edge of screen ...
            self.offsetx, self.offsety =  p.get_window().get_position()
            # plus distance from pointer to edge of widget
            self.offsetx += event.x
            self.offsety += event.y
            # self.maxx, self.maxy both relative to the parent
            # note that we're rounding down now so that these max values don't get
            # rounded upward later and push the widget off the edge of its parent.
            self.maxx = self.RoundDownToMultiple(p.get_allocation().width - w.get_allocation().width, self.SENSITIVITY)
            self.maxy = self.RoundDownToMultiple(p.get_allocation().height - w.get_allocation().height, self.SENSITIVITY)


    def draggingEvent(self, widget, event):
        # x_root,x_root relative to screen
        # x,y relative to parent (fixed widget)
        # self.px,self.py stores previous values of x,y

        # get starting values for x,y
        x = event.x_root - self.offsetx
        y = event.y_root - self.offsety
        # make sure the potential coordinates x,y:
        #   1) will not push any part of the widget outside of its parent container
        #   2) is a multiple of self.SENSITIVITY
        x = self.RoundToNearestMultiple(self.Max(self.Min(x, self.maxx), 0), self.SENSITIVITY)
        y = self.RoundToNearestMultiple(self.Max(self.Min(y, self.maxy), 0), self.SENSITIVITY)
        if x != self.px or y != self.py:
            self.px = x
            self.py = y
            self.desktop.move(widget, x, y)

    def Min(self, a, b):
        if  b < a:
            return b
        return a

    def Max(self, a, b):
        if b > a:
            return b
        return a

    def RoundDownToMultiple(self, i, m):
        return i/m*m

    def RoundToNearestMultiple(self, i, m):
        if i % m > m / 2:
            return (i/m+1)*m
        return i/m*m
