#!/usr/bin/env python

import sys
import os
import neutralContour as nc
import LabelWindow as lw
import AnalysisWindow as aw
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

class LinguaViewer:
    """This is the class for the main window of LinguaViewer"""
    
    def __init__(self, datafiles=[]):
        #self.static_dir = '/Users/jeff/autotracer/trunk/LinguaViewer/'
        self.gladefile = "LinguaViewer.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "mainwindow")
        self.win = self.wTree.get_widget("mainwindow")
        self.win.set_title("LinguaView")
        self.mainVBox = self.wTree.get_widget("vbox2")
        
        dic = { "on_mainwindow_destroy": gtk.main_quit,
                "on_quit_activate" : gtk.main_quit,
                "on_open_activate" : self.onOpen,
                "on_tbOpen_clicked" : self.onOpen,
                "on_tbView_clicked": self.onView,
                "on_tbLabel1_clicked": self.onLabel,
                "on_tbRemove_clicked" : self.onRemove,
                "on_tbAnalyze_clicked" : self.onAnalyze,
                "on_showlinguagram_toggled": self.showlinguagram,
                "on_showneutral_toggled": self.showneutral,
                "on_showwave_toggled": self.showwave,
                "on_showspec_toggled": self.showspec}
                
        self.wTree.signal_autoconnect(dic)
        
        self.SHOW_LING = False
        self.SHOW_NEUT = False
        self.SHOW_WAVE = False
        self.SHOW_SPEC = False
        
        self.linguaToggle = self.wTree.get_widget("showlinguagram")
        self.neutralToggle = self.wTree.get_widget("showneutral")
        self.neutralToggle.set_active(True)
        self.waveToggle = self.wTree.get_widget("showwave")
        self.waveToggle.set_active(True)
        self.specToggle = self.wTree.get_widget("showspec")
        self.specToggle.set_active(True)
        
        self.TreeView = self.wTree.get_widget("treeview1")
        column = gtk.TreeViewColumn("Data Files", gtk.CellRendererText(), text=0)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        self.TreeView.append_column(column)
        self.DataList = gtk.ListStore(str)
        self.TreeView.set_model(self.DataList)
        
        self.datafiles = datafiles
        if len(self.datafiles) > 0:
            for i in self.datafiles:
                self.DataList.append([i])
                
        self.labelInd = 0
        
    def onOpen(self, event):
        fc = gtk.FileChooserDialog(title='Open Data Files', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('.csv Files')
        ffilter.add_pattern('*.csv')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.datafiles = fc.get_filenames()
            g_directory = fc.get_current_folder()
            for i in self.datafiles:
                self.DataList.append([i])
        fc.destroy()

    def onRemove(self, event):
        selection = self.TreeView.get_selection()
        model, select_iter = selection.get_selected()
        if (select_iter):
            self.DataList.remove(select_iter)
    
    def onView(self, event):
        selection = self.TreeView.get_selection()
        model, select_iter = selection.get_selected()
        if (select_iter):
            fname = self.DataList.get_value(select_iter, 0)
            n = fname.split('/')
            neutralfname = '/'.join(n[:-1]) + '/neutral.csv'
            nc.NeutralTongue(fname, neutralfname, self.SHOW_LING, self.SHOW_NEUT, self.SHOW_WAVE, self.SHOW_SPEC)

    def onLabel(self, event):
        selection = self.TreeView.get_selection()
        model, select_iter = selection.get_selected()
        if (select_iter):
            fname = self.DataList.get_value(select_iter, 0)
            n = fname.split('/')
            neutralfname = '/'.join(n[:-1]) + '/neutral.csv'
            lw.LabelWindow([fname], self.SHOW_LING, self.SHOW_NEUT, self.SHOW_WAVE, self.SHOW_SPEC)
                            
    def onAnalyze(self, event):
        aw.AnalysisWindow(self.datafiles)
        
    def showlinguagram(self, event):
        if self.SHOW_LING == False:
            self.SHOW_LING = True
        else:
            self.SHOW_LING = False
        
    def showneutral(self, event):
        if self.SHOW_NEUT == False:
            self.SHOW_NEUT = True
        else:
            self.SHOW_NEUT = False
            
    def showwave(self, event):
        if self.SHOW_WAVE == False:
            self.SHOW_WAVE = True
        else:
            self.SHOW_WAVE = False
        
    def showspec(self, event):
        if self.SHOW_SPEC == False:
            self.SHOW_SPEC = True
        else:
            self.SHOW_SPEC = False
            
            
if __name__ == "__main__":
    LinguaViewer()
    gtk.main()
            