#!/usr/bin/env python

'''
AutoTrace.py
Written by Jeff Berry on Aug 16 2010

purpose:
    This is the main script for the AutoTrace tools.

usage:
    python AutoTrace.py
    
--------------------------------------------------
Modified by Jeff Berry on Feb 21 2011
reason:
    added support for ROI_config.txt, network selection.
--------------------------------------------------
Modified by Jeff Berry on Feb 25 2011
reason:
    added support for unique tracer codes on .traced.txt files
'''

import sys, os, time
import subprocess
import PGLite as pg
import fixImages
import format4R as f4r
import LinguaView as lv
import TrackDots as hc
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import Queue
import threading

CopyQueue = Queue.Queue()

class CopyThread(threading.Thread):        
    def run(self):
        flag = 'ok'
        while (flag != 'stop'):
            cmd = CopyQueue.get()
            if cmd == None:
                flag = 'stop'
            else:
                print ' '.join(cmd)
                p = subprocess.Popen(cmd)
                p.wait()
        print "CopyThread stopped"


class Controller:
    def __init__(self):
        self.app_dir = os.getcwd() 
        self.gladefile = self.app_dir + "/LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "PGController")
        self.win = self.wTree.get_widget("PGController")
        self.win.set_title("AutoTrace")
        
        dic = { "on_PGController_destroy" : gtk.main_quit,
                "on_quit5_activate" : gtk.main_quit,
                "on_open2_activate" : self.onOpen,
                "on_tbOpe_clicked" : self.onOpen,
                "on_tbView1_clicked" : self.onView,
                "on_tbTrace_clicked" : self.onAutoTrace,
                "on_tbExport_clicked" : self.onExport,
                "on_tbNetwork_clicked" : self.onNetwork,
                "on_tbHeadCorr_clicked" : self.onHeadCorr}
                
        self.wTree.signal_autoconnect(dic)
        
        self.TreeView = self.wTree.get_widget("treeview2")
        column = gtk.TreeViewColumn("Image Files", gtk.CellRendererText(), text=0)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        self.TreeView.append_column(column)
        self.DataList = gtk.ListStore(str)
        self.TreeView.set_model(self.DataList)
        self.tmpdirs = []
        self.network = ''
        
    def onHeadCorr(self, event):
        hc.TrackWindow(self.datafiles)

    def onNetwork(self, event):
        nc = gtk.FileChooserDialog(title='Open Network File', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = nc.get_current_folder()
        nc.set_current_folder(g_directory)
        nc.set_default_response(gtk.RESPONSE_OK)
        nc.set_select_multiple(False)
        ffilter = gtk.FileFilter()
        ffilter.set_name('.mat Files')
        ffilter.add_pattern('*.mat')
        nc.add_filter(ffilter)
        response = nc.run()
        if response == gtk.RESPONSE_OK:
            self.network = nc.get_filename()
            g_directory = nc.get_current_folder()
        nc.destroy()        
        
    def onOpen(self, event):
        fc = gtk.FileChooserDialog(title='Open Image Files', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        if not g_directory:
            g_directory = os.path.expanduser('~')
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('.jpg Files')
        ffilter.add_pattern('*.jpg')
        ffilter.add_pattern('*.png')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.datafiles = fc.get_filenames()
            g_directory = fc.get_current_folder()
            for i in self.datafiles:
                self.DataList.append([i])
            fixImages.ImageFixer(self.datafiles)
        fc.destroy()
                
    def onView(self, event):
        # first we need to check whether autotracer.m updated anything
        if (len(self.tmpdirs) > 0):
            tracedfiles = []
            for i in range(len(self.tmpdirs)):
                files = os.listdir(self.tmpdirs[i])
                for j in files:
                    if 'traced.txt' in j: #ok - this just adds the traced.txt to the list
                        tracedfiles.append(j)
                for k in tracedfiles:
                    arg1 = self.tmpdirs[i]+k
                    cmd = ['mv', arg1, self.directories[i]]
                    proc = subprocess.Popen(cmd)
                    proc.wait()
                cmd = ['rm', '-rf', self.tmpdirs[i]]
                proc = subprocess.Popen(cmd)
                
        tcdlg = TracerDialog()        
        result, tracerinfo = tcdlg.run()
        
        if (result == 1):
            try:
                tracer = pg.ImageWindow(self.datafiles, '.'+tracerinfo)
            except AttributeError:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "Error: Please specify files to view")
                md.run()
                md.destroy()
        
                   
    def onAutoTrace(self, event):
        if (self.network == ''):
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, "Error: Please specify a network")
            md.run()
            md.destroy()

        else:
            try:
                l = len(self.datafiles)

                self.directories = self.get_dirs()
                self.tmpdirs = []
            
                self.pathtofiles = self.directories[0]
                self.config = self.pathtofiles + 'ROI_config.txt'
                print self.config
                if (os.path.isfile(self.config)):
                    print "Found ROI_config.txt"
                    c = open(self.config, 'r').readlines()
                    top = int(c[1][:-1].split('\t')[1])
                    bottom = int(c[2][:-1].split('\t')[1])
                    left = int(c[3][:-1].split('\t')[1])
                    right = int(c[4][:-1].split('\t')[1])
                    print "using ROI: [%d:%d, %d:%d]" % (top, bottom, left, right)
                else:
                    print "ROI_config.txt not found"
                    top = 140 #default settings for the Sonosite Titan
                    bottom = 320
                    left = 250
                    right = 580
                    print "using ROI: [%d:%d, %d:%d]" % (top, bottom, left, right)
                roi = str([top, bottom, left, right])
            
                for i in self.directories:
                    #make a tmpdir
                    tmpdir = i + 'autotraceTMP/'
                    self.tmpdirs.append(tmpdir)
                    cmd = ['mkdir', tmpdir]
                    proc = subprocess.Popen(cmd)
                    proc.wait()                
                
                    #copy files
                    for j in self.datafiles:
                        tmpfname = j.split('/')[-1]
                        cmd = ['ln', '-s', j, tmpdir+tmpfname]
                        #CopyQueue.put(cmd)
                        proc = subprocess.Popen(cmd)
                        proc.wait()
                
                    #run AutoTracer.m
                    argstr = "cd " + self.app_dir + "/; AutoTracer('" + tmpdir + "', "  + roi + ", '" + self.network + "'" + "); quit()"
                    print argstr
                    cmd = ['matlab', '-nodesktop', '-nosplash', '-r', argstr] 
                    proc = subprocess.Popen(cmd)
                    proc.wait()
                
                #up to here should be indented if using the cf dialog
            
                fin = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                    gtk.BUTTONS_CLOSE, "AutoTracing completed")
                fin.run()
                fin.destroy()
                    
            except AttributeError:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "Error: Please specify files to trace")
                md.run()
                md.destroy()
        
    def get_dirs(self):
        dirs = {}
        for i in self.datafiles:
            chop = i.split('/')
            chop = chop[:-1]
            d = '/'.join(chop) + '/'
            dirs[d] = 1
        return dirs.keys()            
        
    def onExport(self, event):
        l = len(self.datafiles)
        dir1 = self.get_dirs()[0]
        files = os.listdir(dir1)
        traces = []
        for i in files:
            if ('.traced.txt' in i):
                traces.append(i)
                
        # we're making a lot of assumptions here, i.e. that all traces
        # are in the same directory, and that they all have the same tracer code
        if (len(traces) > 0):
            #check whether there is a tracer code (for old trace files)
            if ( len(traces[0].split('.')) > 4 ):
                self.tracercode = '.' + traces[0].split('.')[-3]
            else:
                self.tracercode = ''
        else:
            self.tracercode = ''
        
        try:
            f = open(self.datafiles[0] + self.tracercode + '.traced.txt', 'r')

            exdlg = ExportDialog()
            result, currentdir, hc, view = exdlg.run()

            if result == 1:
                # Make a Palatoglossatron style output file
                self.formatAutoTrace(hc, currentdir)
            
                # Do Head Correction with peterotron
                if hc == True:
                    #check whether peterotron is compiled
                    if not os.path.isfile('peterotron'):
                        if os.path.isfile('peterotron.c'):
                            print "compiling peterotron"
                            p = subprocess.Popen(['gcc', '-o', 'peterotron', '-lm', 'peterotron.c'])
                            p.wait()
                    if (os.path.isfile('peterotron') and os.path.isfile('settings.txt')):
                        pgoutname =  currentdir + '/Palatoglossatron_Output.txt'
                        p = subprocess.Popen(['mv', pgoutname, '.'])
                        p.wait()
                        p = subprocess.Popen(['./peterotron', 'Palatoglossatron_Output', 'y'])
                        p.wait()
                        print 'peterotron OK'
                        p = subprocess.Popen(['mv', 'Palatoglossatron_Output.txt', currentdir+'/PG_Output_Uncorrected.txt'])
                        p.wait()
                        print 'OK mv1'
                        p = subprocess.Popen(['mv', 'Palatoglossatron_Output_output.txt', currentdir+'/Palatoglossatron_Output.txt'])
                        p.wait()
                        print 'OK mv2'
                            
                # Run format4R.py to get the .csv files
                fname = currentdir + '/Palatoglossatron_Output.txt'
                fnames = f4r.separate(fname)
                csvs = []
                for i in fnames:
                    namelist = i.split('/')
                    name = namelist[-1]
                    newname = currentdir+'/'+name
                    os.system("mv %s %s" %(i, newname))
                    csvs.append(newname)
            
                # Open LinguaViewer.py to view results
                if view == True:
                    lv.LinguaViewer(csvs)
        
        except IOError:
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, "Error: No traces found")
            md.run()
            md.destroy()

    def formatAutoTrace(self, USE_HC, currentdir):
        filename = currentdir + '/Palatoglossatron_Output.txt'
        o = open(filename, 'w')
        o.write("Filename\tRaw.R1.X\tRaw.R1.Y\tRaw.R2.X\tRaw.R2.Y\tRaw.R3.X\tRaw.R3.Y\tRaw.R4.X\tRaw.R4.Y\tRaw.R5.X\tRaw.R5.Y\tRaw.R6.X\tRaw.R6.Y\tRaw.R7.X\tRaw.R7.Y\tRaw.R8.X\tRaw.R8.Y\tRaw.R9.X\tRaw.R9.Y\tRaw.R10.X\tRaw.R10.Y\tRaw.R11.X\tRaw.R11.Y\tRaw.R12.X\tRaw.R12.Y\tRaw.R13.X\tRaw.R13.Y\tRaw.R14.X\tRaw.R14.Y\tRaw.R15.X\tRaw.R15.Y\tRaw.R16.X\tRaw.R16.Y\tRaw.R17.X\tRaw.R17.Y\tRaw.R18.X\tRaw.R18.Y\tRaw.R19.X\tRaw.R19.Y\tRaw.R20.X\tRaw.R20.Y\tRaw.R21.X\tRaw.R21.Y\tRaw.R22.X\tRaw.R22.Y\tRaw.R23.X\tRaw.R23.Y\tRaw.R24.X\tRaw.R24.Y\tRaw.R25.X\tRaw.R25.Y\tRaw.R26.X\tRaw.R26.Y\tRaw.R27.X\tRaw.R27.Y\tRaw.R28.X\tRaw.R28.Y\tRaw.R29.X\tRaw.R29.Y\tRaw.R30.X\tRaw.R30.Y\tRaw.R31.X\tRaw.R31.Y\tRaw.R32.X\tRaw.R32.Y\tUL.x\tUL.y\tUR.x\tUR.y\tLL.x\tLL.y\tLR.x\tLR.y\tAux1.x\tAux1.y\tAux2.x\tAux2.y\tAux3.x\tAux3.y\tAux4.x\tAux4.y\tAux5.x\tAux5.y\tAux6.x\tAux6.y\tAux7.x\tAux7.y\tAux8.x\tAux8.y\tAux9.x\tAux9.y\tAux10.x\tAux10.y\n")
        
        fnames = []
        for i in self.datafiles:
            fnames.append(i + self.tracercode + '.traced.txt')
            
        for i in fnames:
            try:
                f = open(i, 'r').readlines()
                nums = []
                for j in range(len(f)):
                    x = f[j][:-1].split('\t')
                    nums.append(int(round(float(x[1]))))
                    nums.append(int(round(float(x[2]))))

                if USE_HC == True:
                    try:
                        hcname = '.'.join(i.split('.')[0:2]) + '.hc.txt'
                        print hcname
                        hc = open(hcname, 'r').readlines()
                        for k in range(len(hc)):
                            y = hc[k][:-1].split('\t')
                            nums.append(int(round(float(y[1]))))
                            nums.append(int(round(float(y[2]))))
                    except IOError:
                        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_CLOSE, "Error: No hc file found for " + i)
                        md.run()
                        md.destroy()
                else:
                    for k in range(8):
                        nums.append(-1)

                for l in range(20):
                    nums.append(-1)
                o.write('%s' % i[:-11])
                for k in nums:
                	o.write('\t%s' % k)
                o.write('\n')
            except IOError:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "Error: No trace found for " + i)
                md.run()
                md.destroy()
        	    
        o.close()	
            
class ExportDialog:
    def __init__(self):
        self.gladefile = "LinguaViewer.glade"
        self.USE_HC = False
        self.VIEW_RESULTS = False
        
    def run(self):
        self.wTree = gtk.glade.XML(self.gladefile, "dialog1")
        dic = { "on_usehc_toggled" : self.onUse,
                "on_viewresults_toggled" : self.onView}
        self.wTree.signal_autoconnect(dic)
        self.dlg = self.wTree.get_widget("dialog1")
        
        fcbutton = self.wTree.get_widget("filechooserbutton2")
        fcbutton.connect("file-set", self.file_selected)
        self.currentdir = fcbutton.get_current_folder()

        result = self.dlg.run()
        self.dlg.destroy()
        
        return result, self.currentdir, self.USE_HC, self.VIEW_RESULTS
        
    def file_selected(self, widget):
        self.currentdir = widget.get_current_folder()
        
    def onUse(self, event):
        if self.USE_HC == False:
            self.USE_HC = True
        else:
            self.USE_HC = False
            
    def onView(self, event):
        if self.VIEW_RESULTS == False:
            self.VIEW_RESULTS = True
        else:
            self.VIEW_RESULTS = False
            
class TracerDialog:
    def __init__(self):
        self.gladefile = "LinguaViewer.glade"
        
    def run(self):
        self.wTree = gtk.glade.XML(self.gladefile, "get_tracer_info")
        self.dlg = self.wTree.get_widget("get_tracer_info")
        self.tracerentry = self.wTree.get_widget("tracerentry")
        
        result = self.dlg.run()
        
        tracer = self.tracerentry.get_text()
 
        self.dlg.destroy()
        
        return result, tracer


if __name__ == "__main__":
    Controller()
    gtk.main()
