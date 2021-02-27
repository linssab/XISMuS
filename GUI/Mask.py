#################################################################
#                                                               #
#          MASK CLASS FOR CORRELATION PLOTS                     #
#                        version: 2.1.0 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
from matplotlib import patches

class Anchor:
    def __init__(__self__,x,y,w,h,COUNT):
        if x is None or y is None: 
            __self__.dot = None
            return
        __self__.number = COUNT
        __self__.x = x
        __self__.y = y
        if COUNT == 0: color="purple"
        else: color="blue"
        __self__.dot = patches.Rectangle(
                (x-(w*0.5),y-(h*0.5)), width=w, height=h, color=color,snap=False)

def line(anchor00, anchor01):
    x0, y0 = anchor00.x, anchor00.y
    x1, y1 = anchor01.x, anchor01.y
    x = [x0,x1]
    y = [y0,y1]
    coefs = np.polyfit(x, y, 1)
    curve = np.poly1d(coefs)
    x = sorted(x)
    line = curve(np.arange(x[0],x[1]))
    return np.arange(x[0],x[1]), line

def first_anchor(anchors):
    if anchors == []: return
    else: return [anchor for anchor in anchors if anchor.number == 0]

def is_too_close(e,anchors):
    radius = 13
    return any([anchor.dot.contains(e)[0] for anchor in anchors])

def is_complete(e,anchors):
    try: boundary = anchors[0].x*2 
    except: boundary = 5
    if any([anchor.number >= 2 for anchor in anchors]): 
        return first_anchor(anchors)[0].dot.contains(e)[0] 
    else: return

def polygon(anchors):
    vertex = [[anchor.x,anchor.y] for anchor in anchors]
    return patches.Polygon(vertex)
    #return vertex

ZERO = 0.000001
EPSILON = 1

# receive: p1 = (x1,y1) and p2 = (x2,y2) points
#   points in a plane
# return: a and b coeficients for the rect
#   defined by p1 and p2
def rectEq(p1,p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    a = (y1-y2)/((x1-x2)+ZERO)
    b = y1 - a*x1
    return a,b

# receive: p1 = (x1,y1), p2 = (x2,y2), p3 = (x3,y3)
#   and p4 = (x4,y4) points in a plane
# return: 1 if rect segment defined by p1 and p2 is
#   crossing rect segment defined by p2 and p3,
#   0 otherwise.
def isCrossing(p1,p2,p3,p4):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]
    a1, b1 = rectEq(p1,p2)
    a2, b2 = rectEq(p3,p4)
    if a1 == a2:
        return 0
    x = (b2 - b1)/(a1 - a2)
    y = a1*x + b1
    if not (min(x1,x2) <= x and max(x1,x2) >= x):
        return 0
    if not (min(x3,x4) <= x and max(x3,x4) >= x):
        return 0
    return 1

# receive: v a list of points p_i = (x_i, y_i)
#   and a point p = (x,y)
# return: true if p is inside the polygon defined
#  by the points in v, false otherwise
def isInside(v, p0):
    max_x, max_y = 0, 0
    for p in v:
        x, y = p[0], p[1]
        max_x = max(x,max_x)
        max_y = max(y,max_y)
    max_x = max_x
    max_y = max_y
    count1 = 0
    count2 = 0
    count3 = 0
    for i in range(len(v)):
        count1 += isCrossing(v[i], v[(i+1)%len(v)], (p0[0], p0[1]), (max_x + EPSILON, max_y + EPSILON))
        count2 += isCrossing(v[i], v[(i+1)%len(v)], (p0[0], p0[1]), (max_x + 2*EPSILON, max_y + EPSILON))
        count3 += isCrossing(v[i], v[(i+1)%len(v)], (p0[0], p0[1]), (max_x + EPSILON, max_y + 2*EPSILON))
    if (count1 + count2) % 2 == 1:
        return count3 % 2 != 0
    else:
        return count1 % 2 != 0
