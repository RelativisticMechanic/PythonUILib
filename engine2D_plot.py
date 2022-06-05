from cmath import nan

import pygame
import engine2D
import numpy as np
import math

class Point:
    def __init__(self, x, y, z=1):
        self.x = x
        self.y = y
        self.z = z

# Transforms a Cartesian (x,y) point to screen space (x,y)
# Here
# pt - point in question
# x,y - the top left coordinate of the plot space on screen
# w,h - the dimensions of the plot space on screen
# x_start, y_start - minimum Cartesian coordinate allowed on screen
# x_end, y_end - maximum Cartesian coordinate allowed on screen
# returns a (x,y) coordinate
def CartesianToScreen(px, py, x, y, w, h, x_start, x_end, y_start, y_end):
    x_scale = (w) / (x_end - x_start)
    y_scale = (h) / (y_end - y_start)
    
    # the origin of this plot space is the centre of the plot space
    x_origin_plotset = (x_end + x_start) / 2
    y_origin_plotset = (y_end + y_start) / 2

    # the centre of the screen plot space
    x_origin_screen = (x + w*0.5)
    y_origin_screen = (y + h*0.5)

    return (x_origin_screen + (px - x_origin_plotset) * x_scale, y_origin_screen - (py - y_origin_plotset) * y_scale)

def ScreenToCartesian(px, py, x, y, w, h, x_start, x_end, y_start, y_end):
    x_scale = (w) / (x_end - x_start)
    y_scale = (h) / (y_end - y_start)
    
    # the origin of this plot space is the centre of the plot space
    x_origin_plotset = (x_end + x_start) / 2
    y_origin_plotset = (y_end + y_start) / 2

    # the centre of the screen plot space
    x_origin_screen = (x + w*0.5)
    y_origin_screen = (y + h*0.5)
    return (((px - x_origin_screen) / x_scale) + x_origin_plotset, (-(py - y_origin_screen) / y_scale) + y_origin_plotset)

# Plots a set of points on the screen in a given screen space
# Here
# pts - point list of plots to plot
# x,y - the topleft coordinate of the plot space on screen
# w,h - the dimensions of the plot space on scren
# x_start,y_start - which co-ordinate to start plotting from in the given Point collection
# x_end,y_end - final co-ordinates
def PlotPoints(pts, x, y, w, h, x_start, x_end, y_start, y_end, type='LINE', axes=True):
    # We need to scale the Cartesian co-ordinates into screen space
    x_scale = (w) / (x_end - x_start)
    y_scale = (h) / (y_end - y_start)
    
    # the origin of this plot space is the centre of the plot space
    x_origin = (x_end + x_start) / 2
    y_origin = (y_end + y_start) / 2

    # the centre of the screen plot space
    x_origin_screen = (x + w*0.5)
    y_origin_screen = (y + h*0.5)

    # used for the 'LINE' variable to store the previous point
    ox = nan
    oy = nan

    if(axes):
        y_axis = x_origin_screen - x_origin * x_scale
        x_axis = y_origin_screen + y_origin * y_scale
        if(x_axis < y): x_axis = y
        if(y_axis < x): y_axis = x
        if(x_axis > y + h): x_axis = y + h
        if(y_axis > x + w): y_axis = x + w

        engine2D.DrawLine(y_axis, y, y_axis, y+h, 32, 32, 192)
        engine2D.DrawLine(x, x_axis, x+w, x_axis, 32, 32, 192)


    for i in range(0, len(pts)):
        if(pts[i].x > x_end or pts[i].x < x_start):
            continue
        
        # The magic happens here. the point is first translated to fit the plot space
        # then scaled, and then is translated again to fit the screen space.
        px = x_origin_screen + (pts[i].x - x_origin) * x_scale
        # Note: the screen space Y-axis is negative so reverse
        py = y_origin_screen - (pts[i].y - y_origin) * y_scale

        # finally, draw the points if they are still within screen bounds
        if(px > x and py > y and px < (x+w) and py < (y+h)):
            if(type == 'SCATTER'):
                engine2D.DrawPixel(px, py, 255, 255, 255)
            elif(type == 'LINE'):
                if(not math.isnan(ox)):
                    #engine2D.DrawLine(ox, oy, px, py, 255, 255, 255)
                    pygame.draw.aaline(engine2D.GetScreenSurface(), (255, 255, 255), (ox, oy) ,(px, py), 2)
                
                ox = px
                oy = py
    
# Directly creates a plot and plots it
# x,y,w,h - screen space to plot the function
# f - the function itself, must return a double.
# xmin,ymin - minimum xcoordinates
# xmax,ymax - maximum ycoordinates
# step - distance between two x points 0.1 by default
def PlotFunction(f, x, y, w, h, xmin, xmax, ymin, ymax, step=0.1, axes=True):
    PlotPoints([Point(x, f(x)) for x in np.arange(xmin, xmax, step)], x, y, w, h, xmin, xmax, ymin, ymax, 'LINE', axes)