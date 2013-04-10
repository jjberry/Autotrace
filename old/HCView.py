#!/usr/bin/env python

'''
HCView.py
Written by Jeff Berry on Mar 3 2011

purpose:
    this is a helper file for TrackDots.py. The algorithms for
    displaying and correcting the palatoglossatron dots are 
    contained here.
    
usage:
    from TrackDots.py - this script should not be run directly
    by the user.
    
'''


import os, subprocess
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import os, sys, time
import gnomecanvas
from math import *
from numpy import *
import cv


class ImageWindow:
    def __init__(self, imagefiles, independent=True):
        self.pathtofiles = '/'.join(imagefiles[0].split('/')[:-1]) + '/'
        self.imagefiles = imagefiles
        self.INDEPENDENT = independent
        self.mouse_down = False
        self.filenamesind = 0
        self.close_enough = False
        
        self.gladefile = "trackdots.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "HCView")
        self.window = self.wTree.get_widget("HCView")
        
        sigs = {"on_tbNext_clicked" : self.onNext,
                "on_tbPrev_clicked" : self.onPrev,
                "on_HCView_destroy" : self.onDestroy}
        self.wTree.signal_autoconnect(sigs)
        
        self.hbox = self.wTree.get_widget("hbox2")
        self.statusbar = self.wTree.get_widget("statusbar2")
        
        img = cv.LoadImageM(self.imagefiles[0], iscolor=False)
        self.csize = shape(img)
        
        self.canvas = gnomecanvas.Canvas(aa=True)
        self.canvas.set_size_request(self.csize[1], self.csize[0])
        self.canvas.set_scroll_region(0, 0, self.csize[1], self.csize[0])

        # Put it together
        self.hbox.add(self.canvas)
        self.window.set_resizable(False)
        self.window.show_all()
        
        self.canvas.connect("event", self.canvas_event)
        
        self.DrawPoints(self.filenamesind)
        
    def onNext(self, event):
        listlen = len(self.imagefiles)
        self.savePoints(self.filenamesind)
        self.filenamesind = (self.filenamesind + 1) % listlen
        self.DrawPoints(self.filenamesind)
        
        
    def onPrev(self, event):
        listlen = len(self.imagefiles)
        self.savePoints(self.filenamesind)
        if self.filenamesind == 0:
            self.filenamesind = listlen - 1
        else:
            self.filenamesind = self.filenamesind - 1
        self.DrawPoints(self.filenamesind)
        
        
    def onDestroy(self, event):
        self.savePoints(self.filenamesind)
        if self.INDEPENDENT:
            gtk.main_quit()
        else:
            self.window.destroy()

    def canvas_event(self, widget, event):
        if (event.type == gtk.gdk.MOTION_NOTIFY):
            context_id = self.statusbar.get_context_id("mouse motion")
            text = "(" + str(event.x) + ", " + str(event.y) + ")"
            self.statusbar.push(context_id, text) 
            if (self.mouse_down and self.close_enough):
                self.points[self.selected_ind].set(x1=event.x-2, y1=event.y-2, x2=event.x+2, y2=event.y+2)
        elif (event.type == gtk.gdk.KEY_PRESS):
            self.onKeyPress(widget, event) 
        elif (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.mouse_down = True
                ind, dist = self.find_distance(event.x, event.y)
                if dist < 5.0:
                    self.selected_ind = ind
                    self.close_enough = True
        elif ((event.type == gtk.gdk.BUTTON_RELEASE) and self.mouse_down):
            self.mouse_down = False
            self.close_enough = False
            self.point_values[self.selected_ind] = [event.x, event.y]
                
    def find_distance(self, x, y):
        ind = 0
        dist = 999999999.0
        for i in range(len(self.point_values)):
            this_dist = sqrt( (x-self.point_values[i][0])**2 + (y-self.point_values[i][1])**2 )
            if this_dist < dist:
                dist = this_dist
                ind = i
        return ind, dist

    def onKeyPress(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        #print "Key %s (%d) was pressed" % (keyname, event.keyval)
        if keyname == 'Right':
            self.onNext(event)
        elif keyname == 'Left':
            self.onPrev(event)
        else:
            return True

    def set_canvas_background(self, location):
        pixbuf = gtk.gdk.pixbuf_new_from_file(location)
        itemType = gnomecanvas.CanvasPixbuf
        self.background = self.canvas.root().add(itemType, x=0, y=0, pixbuf=pixbuf)

            
    def DrawPoints(self, ind):
        self.window.set_title(self.imagefiles[ind])
        self.set_canvas_background(self.imagefiles[ind])
        self.point_values = []
        self.points = []
        p = open(self.imagefiles[ind]+'.hc.txt', 'r').readlines()
        for i in range(len(p)):
            x = round(float(p[i][:-1].split('\t')[1])) 
            y = round(float(p[i][:-1].split('\t')[2])) 
            self.point_values.append([x, y])
            self.points.append(self.canvas.root().add(gnomecanvas.CanvasEllipse, x1=x-2, y1=y-2, \
                x2=x+2, y2=y+2, fill_color_rgba=0xFFFF00FF, width_units=2.0))
        
    def savePoints(self, ind):
        p = open(self.imagefiles[ind]+'.hc.txt', 'w')
        for i in range(len(self.point_values)):
            p.write("%d\t%f\t%f\n" % (i+1, self.point_values[i][0], self.point_values[i][1]))
        p.close()     
             
                
if __name__ == "__main__":
    ImageWindow()
    gtk.main()
