#!/usr/bin/env python

'''
FileRename.py
Written by Jeff Berry on Jan 14 2011

purpose:
    assists the user in adding experiment, subject and tracer information to files
    
usage:
    python FileRename.py
    
--------------------------------------------------
Modified by Jeff Berry on Feb 25 2011
reason:
    added support for unique tracer codes on .traced.txt files
'''

import os, subprocess
import gtk
import gtk.glade

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
        self.tracerentry = self.wTree.get_widget("entry3")
        
    def openSource(self, event):
        fc = gtk.FileChooserDialog(title='Select Files to Rename', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Image and Trace files')
        ffilter.add_pattern('*.jpg')
        ffilter.add_pattern('*.traced.txt')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.srcfilelist = fc.get_filenames()
            g_directory = fc.get_current_folder()
            self.srcfileentry.set_text(g_directory)
        fc.destroy()
        
    def openDest(self, event):
        fc = gtk.FileChooserDialog(title='Select Save Destination', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
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
        tracer = self.tracerentry.get_text()
        logfile = open(self.dstpath+'log.txt', 'w')
        for i in self.srcfilelist:
            shortname = i.split('/')[-1]
            itemname = shortname.split('_')[0]
            framenumber = (shortname.split('_')[1]).split('.')[0] + '.jpg' 
            if (len((shortname.split('_')[1]).split('.')) > 2):
                dstname = self.dstpath + str(studycode) + str(subjnum) + itemname + '_' + framenumber + '.' + tracer + '.traced.txt'
            else:
                dstname = self.dstpath + str(studycode) + str(subjnum) + itemname + '_' + framenumber 
            print 'renaming', i, '->', dstname 
            logfile.write('%s -> %s\n' %(i, dstname))
            cmd = ['cp', i, dstname]
            p = subprocess.Popen(cmd)
            p.wait()
        logfile.close()
        print "log file saved to", self.dstpath+'log.txt'
        print "done"
        
if __name__ == "__main__":
    FileRename()
    gtk.main()
    
