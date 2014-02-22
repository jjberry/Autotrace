#!/usr/bin/env python

'''
SelectROI.py
Written by Jeff Berry 18 Feb 2011
Modified by Gus Hahn-Powell 21 Feb 2014

purpose:
    This script is designed to help the user select a region of interest
    to use with the set of images selected by the user. The boundaries
    can be set either by clicking and dragging, or with the text entry 
    boxes. When this script is run, it will look for a config file called
    ROI_config.txt that specifies the region of interest. If no such file
    exists, it will be created when the user presses 'Save'. Saving will
    overwrite any previous information in ROI_config.txt.
    ROI_config.txt will be used by other scripts, such as image_diversity.py, 
    Autotrace.py, and TrainNetwork.py.
    
usage:
    python SelectROI.py
'''

import cv
import os, sys
import subprocess
import numpy
from numpy import *
import gtk
import gtk.glade
import gnomecanvas

class ImageWindow:
    def __init__(self):
        self.onOpen()
        self.wTree = gtk.glade.XML("roi.glade", "window1")
        self.window = self.wTree.get_widget("window1")
        
        sigs = {"on_window1_destroy" : gtk.main_quit,
                "on_button1_clicked" : self.onSave,
                "on_button2_clicked" : self.onReset,
                "on_topentry_activate" : self.resetByText,
                "on_bottomentry_activate" : self.resetByText,
                "on_leftentry_activate" : self.resetByText,
                "on_rightentry_activate" : self.resetByText}
        self.wTree.signal_autoconnect(sigs)
        
        self.statusbar = self.wTree.get_widget("statusbar1")
        self.machineCBox = self.wTree.get_widget("combobox1")
        self.machineCBox.set_active(-1) #initialize as "UNKNOWN"
        self.topentry = self.wTree.get_widget("topentry")
        self.bottomentry = self.wTree.get_widget("bottomentry")
        self.leftentry = self.wTree.get_widget("leftentry")
        self.rightentry = self.wTree.get_widget("rightentry")
        
        self.cbox = self.wTree.get_widget("canvashbox")
        self.canvas = gnomecanvas.Canvas(aa=True)
        
        #open an image to see the size
        img = cv.LoadImageM(self.datafiles[0], iscolor=False)
        self.csize = shape(img)
        
        self.canvas.set_size_request(self.csize[1], self.csize[0])
        self.canvas.set_scroll_region(0, 0, self.csize[1], self.csize[0])
        self.cbox.add(self.canvas)
        self.canvas.connect("event", self.canvas_event)
        
        self.DRAG = False
        
        self.pathtofiles = '/'.join(self.datafiles[0].split('/')[:-1]) + '/'

        #Read ROI_config.txt if it exists
        #self.config = os.path.join(self.pathtofiles, 'ROI_config.txt')
        self.config = 'ROI_config.txt'
        #if (os.path.isfile(self.config)):
        if os.path.isfile(os.path.join(self.pathtofiles, self.config)):
            c = open(self.config, 'r').readlines()
            self.top = int(c[1][:-1].split('\t')[1])
            self.bottom = int(c[2][:-1].split('\t')[1])
            self.left = int(c[3][:-1].split('\t')[1])
            self.right = int(c[4][:-1].split('\t')[1])
        else:
            self.top = 140 #default settings for the Sonosite Titan
            self.bottom = 320
            self.left = 250
            self.right = 580
        
        self.getSumImage()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.pathtofiles+'SumImage.png')
        self.background = self.canvas.root().add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=pixbuf)
        
        self.reset()
        subprocess.Popen(['rm', self.pathtofiles+'SumImage.png'])
        
        self.window.show_all()
        
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
            self.datafiles = fc.get_filenames()
            g_directory = fc.get_current_folder() #set this to an attribute?
        fc.destroy()
        
    def onSave(self, event):
        #maybe there should be an overwrite warning???
        #if (os.path.isfile(self.config)):
        model = self.machineCBox.get_model()
        index = self.machineCBox.get_active()
        machine = model[index][0] 
        fc = gtk.FileChooserDialog(title='Save RoI Config File', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SAVE, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        fc.set_current_name(self.config) #sets a suggested filename
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(False)
        fc.set_do_overwrite_confirmation(True)
        response = fc.run()
        #exit fc on cancel..
        if response == gtk.RESPONSE_CANCEL:
            fc.destroy()
        #save...
        if response == gtk.RESPONSE_OK:
            savename = fc.get_filename()
            f_path, f_name = os.path.split(savename)
            o = open(savename, 'w')
            o.write('machine\t%s\n' % machine)
            o.write('top\t%s\n' % self.topentry.get_text())
            o.write('bottom\t%s\n' % self.bottomentry.get_text())
            o.write('left\t%s\n' % self.leftentry.get_text())
            o.write('right\t%s\n' % self.rightentry.get_text())
            o.close()
            dialog = gtk.MessageDialog(parent=None, type=gtk.MESSAGE_INFO, 
                buttons=gtk.BUTTONS_CLOSE, message_format="{roi_config} saved to {path}".format(roi_config=f_name, path=f_path))
            dialog.set_title("Save confirmation")
        dialog.add_button("Exit Program", 100) #100 is an arbitrary choice...
        response = dialog.run()
        #if we want to exit the program...
        if response == 100:
            gtk.main_quit()
        #if we just want to exit fc...
        else:
            dialog.destroy()
            fc.destroy()

    def onReset(self, event):
        self.reset()
        
    def reset(self):
        try:
            self.rubberband.destroy()
        except AttributeError:
            pass
        self.rubberband = self.get_rect(self.left, self.top)
        self.rubberband.set(x2=self.right, y2=self.bottom)
        self.topentry.set_text(str(self.top))
        self.bottomentry.set_text(str(self.bottom))
        self.leftentry.set_text(str(self.left))
        self.rightentry.set_text(str(self.right))
        
    def resetByText(self, event):
        top = int(self.topentry.get_text())
        bottom = int(self.bottomentry.get_text())
        left = int(self.leftentry.get_text())
        right = int(self.rightentry.get_text())
        try:
            self.rubberband.destroy()
        except AttributeError:
            pass
        self.rubberband = self.get_rect(left, top)
        self.rubberband.set(x2=right, y2=bottom)
               
    def canvas_event(self, widget, event):
        if (event.type == gtk.gdk.MOTION_NOTIFY):
            context_id = self.statusbar.get_context_id("mouse motion")
            text = "({x},{y})".format(x=int(event.x), y=int(event.y))
            self.statusbar.push(context_id, text)  
            if (self.DRAG):
                self.rubberband.set(x2=event.x, y2=event.y)

        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                self.rubberband.destroy()
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
                if (self.starty <= self.endy):
                    self.topentry.set_text(str(int(self.starty)))
                    self.bottomentry.set_text(str(int(self.endy)))
                else:
                    self.topentry.set_text(str(int(self.endy)))
                    self.bottomentry.set_text(str(int(self.starty)))
                if (self.startx <= self.endx):
                    self.leftentry.set_text(str(int(self.startx)))
                    self.rightentry.set_text(str(int(self.endx)))
                else:
                    self.leftentry.set_text(str(int(self.endx)))
                    self.rightentry.set_text(str(int(self.startx)))
        
    def get_rect(self, x, y):
        itemType = gnomecanvas.CanvasRect
        rect = self.canvas.root().add(itemType, x1=x, y1=y, x2=x, y2=y, #0x0 dimensions at first
        				fill_color_rgba=0xFFFF0000, outline_color_rgba=0xFFFF0055, width_units=1.0)
        return rect        
        
    def getSumImage(self):
        sum_img = zeros(self.csize)
        for i in self.datafiles:
            img = cv.LoadImageM(i, iscolor=False)   
            tmp = zeros(self.csize)
            tmp += img
            sum_img += tmp 
        #sum_img = (sum_img * 255)/(numpy.max(sum_img))
        sum_img = sum_img/len(self.datafiles)
        cv.SaveImage(self.pathtofiles+'SumImage.png', cv.fromarray(sum_img))   
        self.sum_img = sum_img
        
        
    
if __name__ == "__main__":
    ImageWindow()
    gtk.main()
   
