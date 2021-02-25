import numpy as np
from matplotlib import patches

global NUMBER
NUMBER = 0

class Anchor:
    def __init__(__self__,x,y,w,h):
        global NUMBER
        __self__.number = NUMBER
        __self__.x = x
        __self__.y = y
        __self__.dot = patches.Rectangle(
                (x-(w*0.5),y-(h*0.5)), width=w, height=h, color="blue",snap=False)
        print(NUMBER)
        NUMBER += 1

def line(anchor00, anchor01):
    x0, y0 = anchor00.x, anchor00.y
    x1, y1 = anchor01.x, anchor01.y
    x = [x0,x1]
    y = [y0,y1]
    coefs = np.polyfit(x, y, 1)
    curve = np.poly1d(coefs)
    line = curve(np.arange(0,LEVELS+1))
    line[0:x0] = y0
    line[x1:LEVELS+1] = y1
    return line

def first_anchor(anchors):
    if anchors == []: return
    else: return [anchor for anchor in anchors if anchor.number == 0]

def is_too_close(e,anchors):
    radius = 10
    return any([anchor.dot.contains(e)[0] for anchor in anchors])

def is_complete(e,anchors):
    global NUMBER
    boundary = 4
    if NUMBER < 3: return
    return first_anchor(anchors)[0].dot.contains(e)[0]

