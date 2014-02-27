#!/usr/bin/env python

'''
TrackDots.py
Written by Jeff Berry on Mar 3 2011

purpose:
    This script, together with HCView.py, helps the user to locate 
    the positions of the palatron dots in the subject profile images.
    After the positions are calculated automatically, they are 
    displayed and correction can be done with the mouse if needed.
    
usage:
    python TrackDots.py
    
    In the first window that appears with the thresholded images, 
    select 4 rectangles with the mouse in the order top-left, 
    top-right, bottom-left, bottom-right.
'''

import cv
import os, sys, subprocess
import numpy as np
from numpy import *
import gtk
import gtk.glade
import gnomecanvas
import HCView

class TrackWindow:
    def __init__(self, imagefiles=[]):
        self.imagefiles = imagefiles
        if (len(self.imagefiles) == 0):
            self.INDEPENDENT = True
            self.onOpen()
        else:
            self.INDEPENDENT = False
        self.background = self.getAllThresh(self.imagefiles)
        
        self.gladefile = "trackdots.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "window1")
        self.window = self.wTree.get_widget("window1")
        
        sigs = {"on_ok_clicked" : self.onOK,
                "on_window1_destroy" : self.onDestroy}
        self.wTree.signal_autoconnect(sigs)
        
        self.statusbar = self.wTree.get_widget("statusbar1")
        self.cbox = self.wTree.get_widget("canvashbox")
        self.canvas = gnomecanvas.Canvas(aa=True)
        
        img = cv.LoadImageM(self.background, iscolor=False)
        self.csize = shape(img)
        
        self.canvas.set_size_request(self.csize[1], self.csize[0])
        self.canvas.set_scroll_region(0, 0, self.csize[1], self.csize[0])
        self.cbox.add(self.canvas)
        self.canvas.connect("event", self.canvas_event)

        pixbuf = gtk.gdk.pixbuf_new_from_file(self.background)
        bg = self.canvas.root().add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=pixbuf)

        self.DRAG = False        
        self.pathtofiles = '/'.join(self.imagefiles[0].split('/')[:-1]) + '/'
        self.Rectangles = []
        self.RectanglePoints = []
        for r in range(4):
            self.Rectangles.append(self.get_rect(1,1))
            self.RectanglePoints.append([1,1,1,1])
        self.currentRect = 0
 
        self.window.show_all() 
        
        self.context_id = self.statusbar.get_context_id("instructions")
        text = "Select the rectangles for each dot"
        self.statusbar.push(self.context_id, text)
                       
    def canvas_event(self, widget, event):
        if (event.type == gtk.gdk.MOTION_NOTIFY):
            context_id = self.statusbar.get_context_id("mouse motion")
            text = "(" + str(int(event.x)) + ", " + str(int(event.y)) + ")"
            self.statusbar.push(context_id, text)
            if (self.DRAG):
                self.rubberband.set(x2=event.x, y2=event.y)

        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.Rectangles[self.currentRect].destroy()
                self.DRAG = True
                self.startx = event.x
                self.starty = event.y
                self.rubberband = self.get_rect(self.startx, self.starty)

        # sends selection data to the relevant method
        if (event.type == gtk.gdk.BUTTON_RELEASE) and (self.DRAG):
            if (event.button == 1):
                self.DRAG = False
                self.endx = event.x
                self.endy = event.y
                self.rubberband.set(x2=self.endx, y2=self.endy)
                self.Rectangles[self.currentRect] = self.rubberband
                self.RectanglePoints[self.currentRect] = [self.startx, self.starty, self.endx, self.endy]
                self.currentRect = (self.currentRect + 1) % 4
                
    def get_rect(self, x, y):
        itemType = gnomecanvas.CanvasRect
        rect = self.canvas.root().add(itemType, x1=x, y1=y, x2=x, y2=y, #0x0 dimensions at first
        				fill_color_rgba=0xFFFF0000, outline_color_rgba=0xFFFF00FF, width_units=1.0)
        return rect        
    

    def onOK(self, event):
        prevpoints = [[0,0],[0,0],[0,0],[0,0]]
        for i in self.imagefiles:
            points = self.do1Image(i, prevpoints)
            prevpoints = points
            outputfile = i + '.hc.txt'
            o = open(outputfile, 'w')
            for i in range(4):
                o.write("%d\t%f\t%f\n" % (i+1, points[i][0], points[i][1]))
            o.close()
        HCView.ImageWindow(self.imagefiles, self.INDEPENDENT)
        
    def onDestroy(self, event):
        if os.path.isfile(self.pathtofiles + 'Thresholded.png'):
            p = subprocess.Popen(['rm', self.pathtofiles + 'Thresholded.png'])
            p.wait()
        if self.INDEPENDENT:
            gtk.main_quit()
        else:
            self.window.destroy()

    def onOpen(self):
        fc = gtk.FileChooserDialog(title='Open Image Files', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Image Files')
        ffilter.add_pattern('*.jpg')
        ffilter.add_pattern('*.png')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.imagefiles = fc.get_filenames()
            g_directory = fc.get_current_folder()
        fc.destroy()

    
    def getThreshold(self, image):
        #http://www.aishack.in/2010/07/tracking-colored-objects-in-opencv/
        #http://nashruddin.com/OpenCV_Region_of_Interest_(ROI)
        img = cv.LoadImage(image)
        imgHSV = cv.CreateImage(cv.GetSize(img), 8, 3)
        cv.CvtColor(img, imgHSV, cv.CV_BGR2HSV)
        # Since our pink/red values are from h=0-20 and h=160-179, we have to do thresholding in 
        # two steps...maybe there is an easier way...
        imgThreshed1 = cv.CreateImage(cv.GetSize(img), 8, 1)
        imgThreshed2 = cv.CreateImage(cv.GetSize(img), 8, 1)
        cv.InRangeS(imgHSV, cv.Scalar(0, 50, 50), cv.Scalar(20, 255, 255), imgThreshed1)
        cv.InRangeS(imgHSV, cv.Scalar(160, 50, 50), cv.Scalar(179, 255, 255), imgThreshed2)
        imgThreshed = cv.CreateImage(cv.GetSize(img), 8, 1)
        cv.Or(imgThreshed1, imgThreshed2, imgThreshed)
        return imgThreshed
    
    def getAllThresh(self, imgs):
        # open 1 image to get the size
        img = cv.LoadImage(imgs[0])
        allThresh = cv.CreateImage(cv.GetSize(img), 8, 1)
    
        for i in imgs:
            print "processing", i
            threshed = self.getThreshold(i)
            tmp = cv.CreateImage(cv.GetSize(img), 8, 1)
            cv.Copy(allThresh, tmp)
            cv.Or(tmp, threshed, allThresh)
        savename = '/'.join(imgs[0].split('/')[:-1]) + '/Thresholded.png'
        cv.SaveImage(savename, allThresh)
        return savename
    
    def do1Image(self, image, prevpoints):
        #http://www.aishack.in/2010/07/tracking-colored-objects-in-opencv/
        #http://nashruddin.com/OpenCV_Region_of_Interest_(ROI)
        #http://opencv-users.1802565.n2.nabble.com/Python-cv-Moments-Need-Help-td6044177.html
        #http://stackoverflow.com/questions/5132874/change-elements-in-a-cvseq-in-python
        img = self.getThreshold(image)
        points = []
        for i in range(4):
            cv.SetImageROI(img, (int(self.RectanglePoints[i][0]), int(self.RectanglePoints[i][1]), 
                                int(self.RectanglePoints[i][2]), int(self.RectanglePoints[i][3])))
            storage = cv.CreateMemStorage(0)
            contours = cv.FindContours(img, storage)
            moments = cv.Moments(contours)
            moment10 = cv.GetSpatialMoment(moments, 1, 0)
            moment01 = cv.GetSpatialMoment(moments, 0, 1)
            area = cv.GetCentralMoment(moments, 0, 0)
            cv.ResetImageROI(img)
            if (area != 0):            
                x = self.RectanglePoints[i][0] + (moment10/area)
                y = self.RectanglePoints[i][1] + (moment01/area)   
            else:
                if (prevpoints[i][0] == 0):
                    x = self.RectanglePoints[i][0]
                    y = self.RectanglePoints[i][1]
                else:
                    x = prevpoints[i][0]
                    y = prevpoints[i][1]  
            points.append([x,y])       
        return points
            
            
if __name__ == "__main__":
    TrackWindow()
    gtk.main()
    
