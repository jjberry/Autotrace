#!/usr/bin/env python

'''
PGLite.py
Written by Jeff Berry on Aug 16 2010

purpose:
    This script is an adaptation of Adam Baker's Palatoglossatron. 
    It does all the tracing of tongue images.

usage:
    controlled from AutoTrace.py

--------------------------------------------------
Modified by Jeff Berry on Feb 21 2011
reason:
    updated to automatically detect image size and read machine
    type from ROI_config.txt. 
--------------------------------------------------
Modified by Jeff Berry on Feb 25 2011
reason:
    added support for unique tracer codes on .traced.txt files
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
    def __init__(self, filenames, tracerinfo):
        # Create window
        self.gladefile = "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "PGLite")
        self.window = self.wTree.get_widget("PGLite")
        self.window.connect('destroy', self.onDestroy)

        self.filenamesind = 0   
        self.filenames = filenames   
        self.interpolated = []
        for i in self.filenames:
            self.interpolated.append(False)  
            #self.interpolated.append(True)

        self.tracercode = tracerinfo #for new files
        self.get_tracenames() #for existing files
    
        self.bootstrapList = []
        self.bootstrapCounter = 0

        self.bootstrapDisplay = self.wTree.get_widget("bootstrapentry")        
        self.hbox = self.wTree.get_widget("hbox2")
        self.statusbar = self.wTree.get_widget("statusbar2")

        # Create 720x480 antialised drawing canvas
        img = cv.LoadImageM(filenames[0], iscolor=False)
        self.csize = shape(img)

        self.canvas = gnomecanvas.Canvas(aa=True)
        self.canvas.set_size_request(self.csize[1], self.csize[0])
        self.canvas.set_scroll_region(0, 0, self.csize[1], self.csize[0])

        # Put it together
        self.hbox.add(self.canvas)
        self.window.set_resizable(False)
        self.window.show_all()

        self.pathtofiles = '/'.join(self.filenames[0].split('/')[:-1]) + '/'
        self.config = self.pathtofiles + 'ROI_config.txt'
        print self.config
        if (os.path.isfile(self.config)):
            print "Found ROI_config.txt"
            c = open(self.config, 'r').readlines()
            self.machine = c[0][:-1].split('\t')[1]
            if self.machine == '':
                self.machine = 'Sonosite Titan'
            print "Using machine: " + self.machine
        else:
            self.machine = 'Sonosite Titan' #default

        # Add new grid definitions here and in the glade file roi.glade
        self.machineOptions = {'Sonosite Titan' : [[115., 167., 357., 392.], [421., 172., 667., 392.]],
                          'Toshiba' : [[155., 187., 286., 437.], [432., 187., 575., 437.]]}

        # Event Handling
        dic = { "on_tbGrid_clicked": self.on_set_grid,
                "on_tbNext_clicked": self.nextImage,
                "on_tbPrev_clicked" : self.prevImage,
                "on_tbBoot_clicked": self.add_to_bootstrap_list}
        self.wTree.signal_autoconnect(dic)

        self.canvas.connect("event", self.canvas_event)
        self.dragging = False
        self.tracing = False
        self.delete_points = False

        self.options = {'set_grid': self.set_grid, 'trace_contour': self.trace_contour}
        self.SET_GRID = False
        self.GRID_EXISTS = False
        self.numGridLines = 32
        self.gridCount = 0

        self.DrawPoints(0)
        
    def get_tracenames(self):
        '''This method will look for existing trace files and create a dictionary to corresponding
        image files. It will only work if all image files are in the same directory
        '''
        self.tracenames = {}
        tracedir = '/'.join(self.filenames[0].split('/')[:-1])+ '/'
        files = os.listdir(tracedir)
        traces = []
        for i in files:
            if ('traced.txt' in i):
                traces.append(tracedir+i)
                
        for i in self.filenames:
            for j in traces:
                if i in j:
                    self.tracenames[i] = j
        
        # decide if we need to make a 'previoustraces' dir
        if (len(traces) > 0):
            oldcode = traces[0].split('.')[-3]
            if (oldcode != 'jpg'):
                if (oldcode != self.tracercode):
                    self.prevdiffdir = '/'.join(traces[0].split('/')[:-1]) + '/previoustraces/'
                    if not os.path.isdir(self.prevdiffdir):
                        os.mkdir(self.prevdiffdir)
                    self.PREV_DIFF = True
                else:
                    self.PREV_DIFF = False
            else:
                self.prevdiffdir = '/'.join(traces[0].split('/')[:-1]) + '/previoustraces/'
                if not os.path.isdir(self.prevdiffdir):
                    os.mkdir(self.prevdiffdir)
                self.PREV_DIFF = True
        else:
            self.PREV_DIFF = False
            
        
    def DrawPoints(self, ind):
        self.window.set_title(self.filenames[ind])
        self.set_canvas_background(self.filenames[ind])
        self.make_grid()
        self.trace_values = []
        self.trace_points = []

        for i in range(self.numGridLines):
            self.trace_values.append(array([-1.,-1.]))
    
        dummypoint = self.canvas.root().add(gnomecanvas.CanvasEllipse, x1=0, y1=0, \
                x2=4, y2=4, fill_color_rgba=0xFF000000, width_units=5.0)
        for i in range(self.numGridLines):
            self.trace_points.append(dummypoint)
        

        if self.interpolated[ind] == False:
            # endpoints are lost during interpolation
            try:
                autotrace = self.interp_trace(self.tracenames[self.filenames[ind]])
            except KeyError:
                pass
            self.interpolated[ind] = True
        else:
            autotrace = []
            try:
                a = open(self.tracenames[self.filenames[ind]], 'r').readlines()
                for j in a:
                    vals = j.split('\t')
                    autotrace.append(array([ float(vals[1]), float(vals[2]) ]))
            except KeyError:
                pass
        try:        
            for i in range(self.numGridLines):
                xc = round(autotrace[i][0])
                yc = round(autotrace[i][1])
                thispoint = MyPoint(xc, yc)
                self.add_point(thispoint, i)
        except UnboundLocalError:
            pass        
            
    def add_to_bootstrap_list(self, event):
        '''this adds the current image to a list of badly traced images that should be used in the next round of training'''
        self.bootstrapList.append(self.filenames[self.filenamesind])
        self.bootstrapCounter += 1
        self.bootstrapDisplay.set_text(str(self.bootstrapCounter))

    def saveBootstrap(self):
        '''writes the bootstrap list to bootstraplist_XXXXXXXXXX.txt'''
        fname = '/'.join(self.filenames[self.filenamesind].split('/')[:-1]) + '/bootstraplist_' + str(time.time()) + '.txt'
        o = open(fname, 'w')
        for i in self.bootstrapList:
            o.write("%s\n" % i)
        o.close()
        
    def onKeyPress(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        #print "Key %s (%d) was pressed" % (keyname, event.keyval)
        if keyname == 'Right':
            self.nextImage(event)
        elif keyname == 'Left':
            self.prevImage(event)
        else:
            return True

    def interp_trace(self, filename):
        # http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        autotrace = open(filename, 'r').readlines()
        output_trace = []
        for i in range(self.numGridLines):
            output_trace.append(array([-1., -1.]))
        input_trace = []
        for i in range(len(autotrace)):
            x = autotrace[i][:-1].split('\t')
            if x[0] != '-1':
                input_trace.append(array([float(x[1]), float(x[2])]))
 
        # check whether we have any data
        if len(input_trace) == 0:
            return output_trace
        
        else:
            #determine whether each gridline intersects the trace
            minx = input_trace[0][0]
            maxx = input_trace[-1][0]
        
            for i in range(len(self.grid_values)):
                gridline = self.grid_values[i]
                leftedge = min(gridline[0],gridline[2])-20
                rightedge = max(gridline[0],gridline[2])+20
            
                segs = []
                for j in input_trace:
                    if (j[0] >= leftedge) and (j[0] <= rightedge):
                        #print i, leftedge, rightedge, j
                        segs.append(j)

                if len(segs) > 0:
                    for k in range(len(segs)-1):
                        C = segs[k]
                        D = segs[k+1]
                        A = array([ gridline[0], gridline[1] ])
                        B = array([ gridline[2], gridline[3] ])
                        E = array([ B[0]-A[0], B[1]-A[1] ])
                        F = array([ D[0]-C[0], D[1]-C[1] ])
                        P = ( -E[1], E[0] )
                        h = ( vdot((A-C), P) / vdot(F, P) )
                    
                        if (h >= 0) and (h <= 1):
                            intersection = C + F*h
                try:
                    output_trace[i] = intersection
                    intersection = array([-1.,-1.])
                except:
                    pass
            return output_trace
        
    def nextImage(self, event):
        listlen = len(self.filenames)
        self.saveTrace(self.filenamesind)
        self.filenamesind = (self.filenamesind + 1) % listlen
        self.DrawPoints(self.filenamesind)
        
    def prevImage(self, event):
        listlen = len(self.filenames)
        self.saveTrace(self.filenamesind)
        if self.filenamesind == 0:
            self.filenamesind = listlen - 1
        else:
            self.filenamesind = self.filenamesind - 1
        self.DrawPoints(self.filenamesind)
                
    def saveTrace(self, ind):
        if len(self.trace_values) > 0:
            if self.PREV_DIFF:
                try:
                    p = subprocess.Popen(['mv', self.tracenames[self.filenames[ind]], self.prevdiffdir])
                    p.wait()
                except KeyError:
                    pass
            self.tracenames[self.filenames[ind]] = self.filenames[ind] + self.tracercode + '.traced.txt'
            o = open(self.filenames[ind] + self.tracercode + '.traced.txt', 'w')
            for i in range(self.numGridLines):
                if self.trace_values[i][0] != -1.:
                    o.write("%d\t%.2f\t%.2f\n" % (i+1, self.trace_values[i][0], self.trace_values[i][1]))
                else:
                    o.write("%d\t%d\t%d\n" % (-1, -1, -1))
            o.close()
    
    def onDestroy(self, event):
        self.saveTrace(self.filenamesind)
        self.saveBootstrap()
        self.window.destroy()
    
    def on_set_grid(self, event):
        self.SET_GRID = True
        self.gridCount = 0
        for i in range(self.numGridLines):
            self.grid[i].destroy()
        self.grid = []
        try:
            self.Lgridline.destroy()
            self.Rgridline.destroy()
        except:
            pass

    # Set and image in the background
    def set_canvas_background(self, location):
        pixbuf = gtk.gdk.pixbuf_new_from_file(location)
        itemType = gnomecanvas.CanvasPixbuf
        self.background = self.canvas.root().add(itemType, x=0, y=0, pixbuf=pixbuf)

    # Returns a referance to a rectangle drawn on the canvas
    def get_line(self, x, y):
        itemType = gnomecanvas.CanvasLine
        line = self.canvas.root().add(itemType, points=[x, y, x+1, y+1], fill_color_rgba=0xFFFF0088, width_units=1.0)
        return line

    # Event handling
    def canvas_event(self, widget, event):     
        if event.type == gtk.gdk.MOTION_NOTIFY:
            context_id = self.statusbar.get_context_id("mouse motion")
            text = "(" + str(event.x) + ", " + str(event.y) + ")"
            self.statusbar.push(context_id, text)  
        elif event.type == gtk.gdk.KEY_PRESS:
            self.onKeyPress(widget, event) 
        if self.SET_GRID == True:
            self.options['set_grid'](widget, event)          
        else:
            self.options['trace_contour'](widget, event)

    def set_grid(self, widget, event):
        # Creates a rubberband on left-click
        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.dragging = True
                self.startx = event.x
                self.starty = event.y
                if self.gridCount == 0:
                    self.Lgridline = self.get_line(self.startx, self.starty)
                else:
                    self.Rgridline = self.get_line(self.startx, self.starty)

        # Updates the rubberband size while a mouse drags
        if (event.type == gtk.gdk.MOTION_NOTIFY) and (self.dragging):
            if self.gridCount == 0:
                self.Lgridline.set(points=[self.startx, self.starty, event.x, event.y])
            else:
                self.Rgridline.set(points=[self.startx, self.starty, event.x, event.y])
                
        # Sends selection data to the relevant method
        if (event.type == gtk.gdk.BUTTON_RELEASE) and (self.dragging):
            if (event.button == 1):
                self.dragging = False
                self.endx = event.x
                self.endy = event.y
                if self.gridCount == 0:
                    self.Lgridline.set(points=[self.startx, self.starty, self.endx, self.endy])
                    self.gridCount = 1
                    #print self.startx, self.starty, self.endx, self.endy
                else:
                    self.Rgridline.set(points=[self.startx, self.starty, self.endx, self.endy])
                    #print self.startx, self.starty, self.endx, self.endy
                    self.SET_GRID = False
                    self.make_grid()
                    
    def make_grid(self):
        # http://www.topcoder.com/tc?module=Static&d1=tutorials&d2=geometry2
        # See Adam Baker's experiment.cpp
        # Find Intersection of Lgridline and Rgridline
        # Lgridline standard form Ax + By = C
        try:
            self.leftpoints = array(self.Lgridline.get_bounds())
        except AttributeError:
            self.leftpoints = array(self.machineOptions[self.machine][0]) 
        Al = self.leftpoints[3] - self.leftpoints[1]
        Bl = self.leftpoints[0] - self.leftpoints[2]
        Cl = (Al*self.leftpoints[0]) + (Bl*self.leftpoints[1])
        
        #Rgridline
        try:
            self.rightpoints = array(self.Rgridline.get_bounds())
        except AttributeError:
            self.rightpoints = array(self.machineOptions[self.machine][1])
        #For some reason y1 and y2 are switched in the call to get_bounds()! (a bug in gnomecanvas?)
        tmp = self.rightpoints[1]
        self.rightpoints[1] = self.rightpoints[3]
        self.rightpoints[3] = tmp
        
        Ar = self.rightpoints[3] - self.rightpoints[1]
        Br = self.rightpoints[0] - self.rightpoints[2]
        Cr = (Ar*self.rightpoints[0]) + (Br*self.rightpoints[1])
        
        det = (Al*Br) - (Ar*Bl)
        
        if det == 0: #this needs to be fixed
            print "Lines are parallel -- try again"
        else:
            intx = ((Br*Cl) - (Bl*Cr))/det
            inty = ((Al*Cr) - (Ar*Cl))/det
            #print "intersection ", intx, inty
            A = array([intx, inty])
            B = array([self.leftpoints[0], self.leftpoints[1]])
            C = array([self.rightpoints[0], self.rightpoints[1]])
            D = array([self.leftpoints[2], self.leftpoints[3]])
            E = array([self.rightpoints[2], self.rightpoints[3]])
            
            AB = B - A
            AC = C - A
            AD = D - A
            AE = E - A
                       
            angle_AB_horizontal = atan2(AB[1], AB[0])
            angle_AC_horizontal = atan2(AC[1], AC[0])

            linelength = linalg.norm(A-B)
            nearlength = linalg.norm(A-D)

            stepAngle = (angle_AB_horizontal - angle_AC_horizontal)/(self.numGridLines-1)
            
            self.grid = []
            self.grid_values = []
            for i in range(self.numGridLines):
                tmpAngle = angle_AB_horizontal-(i*stepAngle)
                tmpX = A[0] + round(linelength * cos(tmpAngle))
                tmpY = A[1] + round(linelength * sin(tmpAngle))

                tmpNearX = A[0] + round(nearlength * cos(tmpAngle))
                tmpNearY = A[1] + round(nearlength * sin(tmpAngle))

                self.grid_values.append(array([tmpNearX, tmpNearY, tmpX, tmpY]))
                self.grid.append(self.canvas.root().add(gnomecanvas.CanvasLine, points=[tmpNearX, tmpNearY, tmpX, tmpY],   \
                        fill_color_rgba=0xFFFF0055, width_units=1.0))


    def trace_contour(self, widget, event):
        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.tracing = True
            elif (event.button == 3):
                self.delete_points = True

        # Updates the rubberband size while a mouse drags
        if (event.type == gtk.gdk.MOTION_NOTIFY):
            #check whether we're close enought to a gridline
            ind, dist = self.find_distance(event)
            if (dist <= 1.5) and self.tracing:
                self.add_point(event, ind)              
            elif (dist <= 1.5) and self.delete_points:
                self.delete_point(ind)
                            
        # Sends selection data to the relevant method
        if (event.type == gtk.gdk.BUTTON_RELEASE) and (self.tracing):
            if (event.button == 1):
                self.tracing = False
        elif (event.type == gtk.gdk.BUTTON_RELEASE) and (self.delete_points):
            if (event.button == 3):
                self.delete_points = False

    def find_distance(self, event):
        ind = 0
        dist = 999999999.0
        
        for i in range(self.numGridLines):
            gridline = self.grid_values[i]
            ABx = gridline[2] - gridline[0]
            ABy = gridline[3] - gridline[1]
            ACx = event.x - gridline[0]
            ACy = event.y - gridline[1]
            cross = (ABx * ACy) - (ABy * ACx)
            mag = sqrt((ABx*ABx) + (ABy*ABy))
            d = abs(cross/mag)
            if d <= dist:
                dist = d
                ind = i
        return ind, dist
        
    def add_point(self, event, ind):
        centerx = event.x
        centery = event.y
        self.trace_values[ind] = array([centerx, centery]) 
        self.trace_points[ind].destroy()
        self.trace_points[ind] = self.canvas.root().add(gnomecanvas.CanvasEllipse, x1=centerx-2, y1=centery-2, \
            x2=centerx+2, y2=centery+2, fill_color_rgba=0xFF0000FF, width_units=2.0)
        
        #print "\ncontour updated"    
        #for i in range(self.numGridLines):
        #    print self.trace_values[i]

    def delete_point(self, ind):
        self.trace_values[ind] = array([-1., -1.])
        self.trace_points[ind].destroy()
        
        #print "\ncontour updated"    
        #for i in range(self.numGridLines):
        #    print self.trace_values[i]
        

class MyPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    
if __name__ == '__main__':
    imageWindow = ImageWindow(sys.argv[1])
    gtk.main()