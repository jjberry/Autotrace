#!/usr/bin/env python

'''
FileRename.py
Rewritten by Gus Hahn-Powell on March 6 2014
based on code written by Jeff Berry circa 2011

purpose:
    assists the user in adding experiment, subject and tracer information to files
    
usage:
    python FileRename.py

image files...
<study-name>_<subject-id>_<item-name>_<frame-number>.<image-extension>

if a trace file...
<study-name>_<subject-id>_<item-name>_<frame-number>.<image-extension>.<tracer-id>_traced.txt      
'''

import os, subprocess
import re
import gtk
import gtk.glade
image_extension_pattern = re.compile("(\.jpg|\.png)", re.I)
frame_number_pattern = re.compile("(?<=frame-)?([^_.]+)(?=\.jpg|\.png)", re.I) #also handles older naming conventions...
#image_extension_pattern = re.compile("(\.(png|jpg))", re.IGNORECASE)
tracer_pattern = re.compile("([a-z0-9]+)\.traced", re.I) #some tracers use a number...not jsut initials...
class FileRename:
    '''This file renamer expects the format of the source files to be <name>_<frame>.jpg
        <name> can be a combination of letters and numbers, and <frame> is numbers.
        The program will split on the underscore, so if filenames are not in this format
        the behavior will be unpredictable.
    '''
    def __init__(self):
        gladefile = "FileRename.glade"
        self.wTree = gtk.glade.XML(gladefile, "window1")
        self.win = self.wTree.get_widget("window1")
        self.win.set_title("File Renamer")
        
        dic = { "on_window1_destroy" : gtk.main_quit,
                "on_open1_clicked" : self.openSource,
                "on_open2_clicked" : self.openDest,
                "on_ok_clicked" : self.onOK}
        self.wTree.signal_autoconnect(dic)
        
        self.srcfileentry = self.wTree.get_widget("srcfileentry")
        self.dstfileentry = self.wTree.get_widget("dstfileentry")
        self.studycodeentry = self.wTree.get_widget("entry1")
        self.subjnumentry = self.wTree.get_widget("entry2")
        self.itementry = self.wTree.get_widget("entry3")
        self.tracerentry = self.wTree.get_widget("entry4")

        #set default text
        self.itementry.set_text("??")
        
    def openSource(self, event):
        fc = gtk.FileChooserDialog(title='Select Files to Rename', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Image and Trace files')
        ffilter.add_pattern('*.jpg')
        ffilter.add_pattern('*.png')
        ffilter.add_pattern('*.traced.txt')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.srcfilelist = fc.get_filenames()
            print "source file list: " #debug
            for i in self.srcfilelist: print i #debug
            g_directory = fc.get_current_folder()
            self.srcfileentry.set_text(g_directory)
        fc.destroy()
        
    def openDest(self, event):
        fc = gtk.FileChooserDialog(title='Select Save Destination', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.dstpath = fc.get_current_folder() + '/'
            self.dstfileentry.set_text(self.dstpath)
        fc.destroy()
        
    def onOK(self, event):
        studycode = self.studycodeentry.get_text() 
        subjnum = self.subjnumentry.get_text() 
        item = self.tracerentry.get_text() if self.tracerentry.get_text() else "??"
        tracer = self.tracerentry.get_text()
        logfile = open(self.dstpath+'log.txt', 'w')
        for i in self.srcfilelist:
            shortname = os.path.basename(i)
            image_extension = re.search(image_extension_pattern, i).group(1)
            extension = "traced.txt" if "traced.txt" in shortname else image_extension
            print "shortname: {0}\textension: {1}".format(shortname, extension) #debug
            itemname = shortname.split('_')[2] if (shortname.count("_") >= 3) else item
            framenumber = re.search(frame_number_pattern, shortname).group(1)
            #make basic filename and image name...
            print "studycode: {0}".format(studycode) #debug
            print "subjnum: {0}".format(subjnum) #debug
            print "itemname: {0}".format(itemname) #debug
            print "framenumber: {0}".format(framenumber) #debug
            f_basename = str(studycode) + "_" + str(subjnum) + "_" + itemname + "_" + framenumber
            image_name = f_basename + image_extension
            #see if this is a trace file...
            if extension == "traced.txt":
                #if tracer isn't specified, find appropriate tracer...
                tracer = self.tracerentry.get_text() if self.tracerentry.get_text() else re.search(tracer_pattern, shortname).group(1).upper()
                traced = '.' + tracer + '.' + extension
            else:
                traced = ""
            #make new file name...
            dstname = self.dstpath + image_name + traced
            print 'renaming', i, '->', dstname 
            logfile.write('%s -> %s\n' %(i, dstname))
            cmd = ['cp', i, dstname]
            p = subprocess.Popen(cmd)
            p.wait()
        logfile.close()
        print "log file saved to", self.dstpath+'log.txt'
        print "done"
        gtk.main_quit()

if __name__ == "__main__":
    FileRename()
    gtk.main()
    
