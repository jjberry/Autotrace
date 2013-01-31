#!/usr/bin/env python

'''
ExtractFrames.py
Written by Jeff Berry on Mar 1 2011

purpose:
    this script provides a simple interface for the user to select
    a .dv file, a corresponding .TextGrid, and an optional item list
    for extracting .wav and .png and/or .jpg files from the labeled
    intervals defined in the .TextGrid file. If the item list has
    the same number of items as the .TextGrid has labeled intervals,
    the extracted files will have the filename specified in the item
    list. This script depends on ffmpeg and ImageMagick.
    
usage:
    python ExtractFrames.py

--------------------------------------------------
'''

import os, sys, subprocess
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade

class Extract:
    def __init__(self):
        gladefile = "Extract.glade"
        self.wTree = gtk.glade.XML(gladefile, "window1")
        self.win = self.wTree.get_widget("window1")
        self.win.set_title("Extract Frames")
        
        dic = { "on_window1_destroy" : gtk.main_quit,
                "on_openvideo_clicked" : self.onOpenVideo,
                "on_opentextgrid_clicked" : self.onOpenTextGrid,
                "on_openstimuli_clicked" : self.onOpenStimuli,
                "on_convertJPG_toggled" : self.onConvertJPG,
                "on_ok_clicked" : self.onOK}
        self.wTree.signal_autoconnect(dic)
        
        self.inputvideoentry = self.wTree.get_widget("inputvideo")
        self.textgridentry = self.wTree.get_widget("textgrid")
        self.stimulilistentry = self.wTree.get_widget("stimuli")
        self.paddingentry = self.wTree.get_widget("padding")
        
        self.inputvideo = ''
        self.textgrid = ''
        self.stimfile = ''
        self.padding = 0
        self.paddingentry.set_text(str(self.padding))
        self.USE_JPG = False
        
    def onConvertJPG(self, event):
        if self.USE_JPG == False:
            self.USE_JPG = True
        else:
            self.USE_JPG = False
        
    def onOpenVideo(self, event):
        fc = gtk.FileChooserDialog(title='Open Video file', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(False)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Video files')
        ffilter.add_pattern('*.dv')
        ffilter.add_pattern('*.avi')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.inputvideo = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.inputvideoentry.set_text(self.inputvideo)
        fc.destroy()
        
    def onOpenTextGrid(self, event):
        fc = gtk.FileChooserDialog(title='Open TextGrid', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(False)
        ffilter = gtk.FileFilter()
        ffilter.set_name('TextGrid files')
        ffilter.add_pattern('*.TextGrid')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.textgrid = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.textgridentry.set_text(self.textgrid)
        fc.destroy()
            
    def onOpenStimuli(self, event):
        fc = gtk.FileChooserDialog(title='Open Item list', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(False)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Text files')
        ffilter.add_pattern('*.txt')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.stimfile = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.stimulilistentry.set_text(self.stimfile)
        fc.destroy()
      
    def onOK(self, event):
        try:
            self.pad = float(self.paddingentry.get_text())
             
            if (self.textgrid != ''):
                self.ParseTextGrid()
            else:
                raise MyError("TextGrid")

            if (self.inputvideo != ''):
                self.outputpath = '/'.join(self.inputvideo.split('/')[:-1]) + '/'
            else:
                raise MyError("Input Video")
            
            self.stimuli = []    
            if (self.stimfile != ''):
                self.ParseStimFile()  
            
            self.SegmentVideo()    
            self.extract()
            
            if self.USE_JPG:
                self.png2jpg()
                
            fin = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                gtk.BUTTONS_CLOSE, "Extraction completed")
            fin.run()
            fin.destroy()
               
        except MyError as e:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, "Error: " + e.value + " not selected")
            md.run()
            md.destroy()
            
        
    def ParseTextGrid(self):
        tgf = open(self.textgrid, 'r').readlines()
        header = 14 #tells how many header lines there are, or where to start
        
        self.intervals = []
        for i in range(header, len(tgf), 4):
            xmin = float((tgf[i+1].strip()).split(' ')[2]) - self.pad
            xmax = float((tgf[i+2].strip()).split(' ')[2]) + self.pad
            label = (tgf[i+3].strip()).split(' ')[2]
            if (label != '""'):
                self.intervals.append([xmin, xmax])
    
    def ParseStimFile(self):
        f = open(self.stimfile, 'r').readlines()
        for i in f:
            self.stimuli.append(i.strip())
    
    def SegmentVideo(self):
        self.outputnames = []
        if (len(self.stimuli) != len(self.intervals)):
            usebase = True
        else:
            usebase = False
        for i in range(len(self.intervals)):
            start = self.getTime(self.intervals[i][0])
            stopt = self.intervals[i][1] - self.intervals[i][0]
            stop = self.getTime(stopt)
            if usebase:
                output = self.outputpath + "item%d.avi" % (i+1)
            else:
                output = self.outputpath + self.stimuli[i] + '.avi'
            self.outputnames.append(output)
            cmd = ['ffmpeg', '-i', self.inputvideo, '-ss', start, '-t', stop, '-vcodec', 'copy', '-acodec', 'copy', output]
            print ' '.join(cmd)
            p = subprocess.Popen(cmd)
            p.wait()

    def getTime(self, time):
        minute = int(time/60)
        second = time%60
        if (minute >= 60):
            hour = minute/60
            minute = minute%60
        else:
            hour = 0
        t = "%02d:%02d:%.3f" %(hour, minute, second)
        return t 

    def extract(self):
        jpgdir = self.outputpath + 'PNG/'
        if not os.path.isdir(jpgdir):
            os.mkdir(jpgdir)
        wavdir = self.outputpath + 'WAV/'
        if not os.path.isdir(wavdir):
            os.mkdir(wavdir)
        
        for i in self.outputnames:
            outname = self.outputpath + 'PNG/' + i.split('/')[-1][:-4] + '_%6d.png'
            cmd = ['ffmpeg', '-i', i, '-f', 'image2', outname]
            p = subprocess.Popen(cmd)
            p.wait()
            wavname = self.outputpath + 'WAV/' + i.split('/')[-1][:-4] + '.wav'
            cmd = ['ffmpeg', '-i', i, '-vn', '-acodec', 'copy', wavname]
            p2 = subprocess.Popen(cmd)
            p2.wait()

    def png2jpg(self):
        jpgdir = self.outputpath + 'JPG/'
        if not os.path.isdir(jpgdir):
            os.mkdir(jpgdir)
        pngs = os.listdir(self.outputpath+'PNG/')
        for i in pngs:
            jpgname = jpgdir + i[:-4] + '.jpg'
            cmd = ['convert', self.outputpath+'PNG/'+i, jpgname]
            print ' '.join(cmd)
            p = subprocess.Popen(cmd)
            p.wait()

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
if __name__ == "__main__":
    Extract()
    gtk.main()
        