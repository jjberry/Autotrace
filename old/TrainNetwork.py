#!/usr/bin/env python

'''
TrainNetwork.py
Written by Jeff Berry Jul 1 2010

purpose:
    Train a translational Deep Belief Network for tracing. The training
    data should be arranged in a folder called Subject<N>, where N is any
    positive integer, such as Subject1. Images are located in Subject1/JPG/
    and should be .jpg files. The traces are in Subject1/TongueContours.csv,
    which can be created using AutoTrace.py or configdir.py. Parameters 
    defining the region of interest should be listed in Subject1/ROI_config.txt,
    otherwise a default ROI will be used. The resulting tDBN will be located
    in savefiles/network<time>.mat.

usage:
    python TrainNetwork.py
---------------------------------------------
Modified by Jeff Berry Feb 19 2011
reason:
    Updated to make use of ROI_config.txt, which should be in the same
    folder as JPG/ and TongueContours.csv
'''

import sys, os
import subprocess
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
  	import gobject
except:
	sys.exit(1)

class TrainNetwork:
    """This is the class for the main window of trainnetwork.py"""
    
    def __init__(self):
        
        #Set the Glade file
        self.gladefile = "TrainNetwork.glade"
        self.wTree = gtk.glade.XML(self.gladefile, "mainWindow")
        
        #Create dictionary of callbacks and connect
        dic = { "on_mainWindow_destroy" : gtk.main_quit,
                "on_open_activate" : self.open_settings,
                "on_save_activate" : self.on_save,
                "on_save_as_activate" : self.save_settings,
                "on_quit_activate" : gtk.main_quit,
                "on_add_data_activate" : self.add_data,
                "on_crossvalbutton_toggled" : self.set_crossval,
                "on_maximgbutton_toggled" : self.practice_run,
                "on_config_layers" : self.config_layers,
                "on_reset_default_activate" : self.reset_network,
                "on_crossvalbutton_toggled" : self.set_crossval,
                "on_train_ultrasound_toggled" : self.set_train_ultrasound,
                "on_train_contours_toggled" : self.set_train_contours,
                "on_train_audio_toggled" : self.set_train_audio,
                "on_train_velum_toggled" : self.set_train_velum,
                "on_train_glottis_toggled" : self.set_train_glottis,
                "on_train_lips_toggled" : self.set_train_lips,
                "on_train_trascription_toggled" : self.set_train_transcription,
                "on_test_ultrasound_toggled" : self.set_test_ultrasound,
                "on_test_contours_toggled" : self.set_test_contours,
                "on_test_audio_toggled": self.set_test_audio,
                "on_test_velum_toggled" : self.set_test_velum,
                "on_test_glottis_toggled" : self.set_test_glottis,
                "on_test_lips_toggled" : self.set_test_lips,
                "on_test_transcription_toggled" : self.set_test_transcription,
                "on_train_clicked" : self.train,
                "on_cancel_clicked" : self.cancel_training }
        self.wTree.signal_autoconnect(dic)
        
        #Add the CommandTextView widget
        sw = self.wTree.get_widget("scrolledwindow")
        sw.set_size_request(-1, 400)
        self.ctv = CommandTextView()
        sw.add(self.ctv)
        sw.show()
        self.ctv.show()
        
        #Set default values
        self.set_defaults()
        
        #set status for grayed out entry boxes
        self.maximgtextentry = self.wTree.get_widget("maximgtextentry")
        self.crossvaltextentry = self.wTree.get_widget("crossvaltextentry")
        self.maximgtextentry.set_text(str(self.MAX_NUM_IMAGES))
        self.maximgtextentry.set_sensitive(False)
        self.crossvaltextentry.set_text(str(self.NFOLDS))
        self.crossvaltextentry.set_sensitive(False)
        
        #Get widgets for settings functions
        self.maximgbutton = self.wTree.get_widget("maximgbutton")
        self.crossvalbutton = self.wTree.get_widget("crossvalbutton")
        self.train_ultrasound = self.wTree.get_widget("train_ultrasound")
        self.train_contours = self.wTree.get_widget("train_contours")
        self.train_audio = self.wTree.get_widget("train_audio")
        self.train_velum = self.wTree.get_widget("train_velum")
        self.train_glottis = self.wTree.get_widget("train_glottis")
        self.train_lips = self.wTree.get_widget("train_lips")
        self.train_transcription = self.wTree.get_widget("train_transcription")
        self.test_ultrasound = self.wTree.get_widget("test_ultrasound")
        self.test_contours = self.wTree.get_widget("test_contours")
        self.test_audio = self.wTree.get_widget("test_audio")
        self.test_velum = self.wTree.get_widget("test_velum")
        self.test_glottis = self.wTree.get_widget("test_glottis")
        self.test_lips = self.wTree.get_widget("test_lips")
        self.test_transcription = self.wTree.get_widget("test_transcription")
        
    #Callback definitions   
    def set_defaults(self):
        self.MAX_NUM_IMAGES = 100
        self.NFOLDS = 5
        self.PRACTICE_RUN = False
        self.USE_CROSSVAL = False
        self.USE_DEFAULT_NET = True
        self.TRAIN_ULTRASOUND = False
        self.TRAIN_CONTOURS = False
        self.TRAIN_AUDIO = False
        self.TRAIN_VELUM = False
        self.TRAIN_GLOTTIS = False
        self.TRAIN_LIPS = False
        self.TRAIN_TRANSCRIPTION = False
        self.TEST_ULTRASOUND = False
        self.TEST_CONTOURS = False
        self.TEST_AUDIO = False
        self.TEST_VELUM = False
        self.TEST_GLOTTIS = False
        self.TEST_LIPS = False
        self.TEST_TRANSCRIPTION = False
        self.LAYER_SIZES = "[size(trainX,2), size(XC,2), size(XC,2), size(XC,2)*5]"
        self.LAYER_TYPES = "{'gaussian', 'sigmoid', 'sigmoid', 'sigmoid'}"    
        self.SAVEFILE = "" 
        self.DATA_DIR = ""
        self.SUBJECT_NUMS = ""            
                 
    def open_settings(self, widget):
        """A file chooser called when user clicks Open"""
        fc = gtk.FileChooserDialog(title='Open Settings File...', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Settings Files')
        ffilter.add_pattern('*.txt')
        fc.add_filter(ffilter)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            settings = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.load_settings(settings)
        fc.destroy()
        
        
    def load_settings(self, settings):
        f = open(settings, 'r').readlines()
        dic = {}
        for i in range(len(f)):
            line2list = f[i][:-1].split('=')
            if len(line2list) == 2:
                dic[line2list[0]] = line2list[1]    
                
        if dic.has_key("MAX_NUM_IMAGES"):
            self.MAX_NUM_IMAGES = int(dic["MAX_NUM_IMAGES"])
            self.maximgtextentry.set_text(str(self.MAX_NUM_IMAGES))
            
        if dic.has_key("NFOLDS"):
            self.NFOLDS = int(dic["NFOLDS"])
            self.crossvaltextentry.set_text(str(self.NFOLDS))
            
        if dic.has_key("PRACTICE_RUN"):
            self.maximgbutton.set_active(self.parseBool(dic["PRACTICE_RUN"]))
                
        if dic.has_key("USE_CROSSVAL"):
            self.crossvalbutton.set_active(self.parseBool(dic["USE_CROSSVAL"]))
            
        if dic.has_key("USE_DEFAULT_NET"):
            self.USE_DEFAULT_NET = self.parseBool(dic["USE_DEFAULT_NET"])
                
        if dic.has_key("TRAIN_ULTRASOUND"):
            self.train_ultrasound.set_active(self.parseBool(dic["TRAIN_ULTRASOUND"]))

        if dic.has_key("TRAIN_CONTOURS"):
            self.train_contours.set_active(self.parseBool(dic["TRAIN_CONTOURS"]))
            
        if dic.has_key("TRAIN_AUDIO"):
            self.train_audio.set_active(self.parseBool(dic["TRAIN_AUDIO"]))
        
        if dic.has_key("TRAIN_VELUM"):
            self.train_velum.set_active(self.parseBool(dic["TRAIN_VELUM"]))

        if dic.has_key("TRAIN_GLOTTIS"):
            self.train_glottis.set_active(self.parseBool(dic["TRAIN_GLOTTIS"]))

        if dic.has_key("TRAIN_LIPS"):
            self.train_lips.set_active(self.parseBool(dic["TRAIN_LIPS"]))
        
        if dic.has_key("TRAIN_TRANSCRIPTION"):
            self.train_transcription.set_active(self.parseBool(dic["TRAIN_TRANSCRIPTION"]))

        if dic.has_key("TEST_ULTRASOUND"):
            self.test_ultrasound.set_active(self.parseBool(dic["TEST_ULTRASOUND"]))

        if dic.has_key("TEST_CONTOURS"):
            self.test_contours.set_active(self.parseBool(dic["TEST_CONTOURS"]))

        if dic.has_key("TEST_AUDIO"):
            self.test_audio.set_active(self.parseBool(dic["TEST_AUDIO"]))

        if dic.has_key("TEST_VELUM"):
            self.test_velum.set_active(self.parseBool(dic["TEST_VELUM"]))

        if dic.has_key("TEST_GLOTTIS"):
            self.test_glottis.set_active(self.parseBool(dic["TEST_GLOTTIS"]))

        if dic.has_key("TEST_LIPS"):
            self.test_lips.set_active(self.parseBool(dic["TEST_LIPS"]))
            
        if dic.has_key("TEST_TRANSCRIPTION"):
            self.test_transcription.set_active(self.parseBool(dic["TEST_TRANSCRIPTION"]))
                
        if dic.has_key("LAYER_SIZES"):
            self.LAYER_SIZES = dic["LAYER_SIZES"]
            
        if dic.has_key("LAYER_TYPES"):
            self.LAYER_TYPES = dic["LAYER_TYPES"]
            
        if dic.has_key("DATA_DIR"):
            self.DATA_DIR = dic["DATA_DIR"]
            
        if dic.has_key("SUBJECT_NUMS"):
            self.SUBJECT_NUMS = dic["SUBJECT_NUMS"]
            
    def parseBool(self, inputstr):
        return inputstr[0].upper() == 'T'        

    def save_settings(self, widget):
        fc = gtk.FileChooserDialog(title='Save Settings File...', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SAVE, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder()
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_do_overwrite_confirmation(True)
        ffilter = gtk.FileFilter()
        ffilter.set_name('Settings Files')
        ffilter.add_pattern('*.txt')
        fc.add_filter(ffilter)

        response = fc.run()
        if response == gtk.RESPONSE_OK:
            self.SAVEFILE = fc.get_filename()
            g_directory = fc.get_current_folder()
            self.save(self.SAVEFILE)
        fc.destroy()          
    
    def on_save(self, widget):
        if self.SAVEFILE != "":
            self.save(self.SAVEFILE)
        else:
            self.save_settings(widget)
        
    def save(self, filename):
        f = open(filename, 'w')
        f.write("MAX_NUM_IMAGES=%d\n" %self.MAX_NUM_IMAGES)
        f.write("NFOLDS=%d\n" %self.NFOLDS)
        f.write("PRACTICE_RUN=%s\n" %str(self.PRACTICE_RUN))
        f.write("USE_CROSSVAL=%s\n" %str(self.USE_CROSSVAL))
        f.write("USE_DEFAULT_NET=%s\n" %str(self.USE_DEFAULT_NET))
        f.write("TRAIN_ULTRASOUND=%s\n" %str(self.TRAIN_ULTRASOUND))
        f.write("TRAIN_CONTOURS=%s\n" %str(self.TRAIN_CONTOURS))
        f.write("TRAIN_AUDIO=%s\n" %str(self.TRAIN_AUDIO))
        f.write("TRAIN_VELUM=%s\n" %str(self.TRAIN_VELUM))
        f.write("TRAIN_GLOTTIS=%s\n" %str(self.TRAIN_GLOTTIS))
        f.write("TRAIN_LIPS=%s\n" %str(self.TRAIN_LIPS))
        f.write("TRAIN_TRANSCRIPTION=%s\n" %str(self.TRAIN_TRANSCRIPTION))
        f.write("TEST_ULTRASOUND=%s\n" %str(self.TEST_ULTRASOUND))
        f.write("TEST_CONTOURS=%s\n" %str(self.TEST_CONTOURS))
        f.write("TEST_AUDIO=%s\n" %str(self.TEST_AUDIO))
        f.write("TEST_VELUM=%s\n" %str(self.TEST_VELUM))
        f.write("TEST_GLOTTIS=%s\n" %str(self.TEST_GLOTTIS))
        f.write("TEST_LIPS=%s\n" %str(self.TEST_LIPS))
        f.write("TEST_TRANSCRIPTION=%s\n" %str(self.TEST_TRANSCRIPTION))
        f.write("LAYER_SIZES=%s\n" %self.LAYER_SIZES)
        f.write("LAYER_TYPES=%s\n" %self.LAYER_TYPES)
        f.write("DATA_DIR=%s\n" %self.DATA_DIR)
        f.write("SUBJECT_NUMS=%s\n" %self.SUBJECT_NUMS)
        
        f.close()
        
    def get_max_images(self):
        if self.PRACTICE_RUN == True:
            self.MAX_NUM_IMAGES = int(self.maximgtextentry.get_text())
        
        return self.MAX_NUM_IMAGES
        
    def get_nFolds(self):
        if self.USE_CROSSVAL == True:
            self.NFOLDS = int(self.crossvaltextentry.get_text())
            
        return self.NFOLDS
                          
    def set_crossval(self, widget):
        """Called when user clicks Cross validation in Configure menu"""
        if self.USE_CROSSVAL == False:
            self.USE_CROSSVAL = True
            self.crossvaltextentry.set_sensitive(True)
        else:
            self.USE_CROSSVAL = False
            self.crossvaltextentry.set_sensitive(False)
        
    def practice_run(self, widget):
        """Called when user clicks Practice run in Configure menu
           Changes PRACTICE_RUN value and prompts user to set max images
        """
        if self.PRACTICE_RUN == False:
            self.PRACTICE_RUN = True
            self.maximgtextentry.set_sensitive(True)
        else:
            self.PRACTICE_RUN = False
            self.maximgtextentry.set_sensitive(False)

    def reset_network(self, widget):
        self.USE_DEFAULT_NET = True
        self.LAYER_SIZES = "[size(trainX,2), size(XC,2), size(XC,2), size(XC,2)*5]"
        self.LAYER_TYPES = "{'gaussian', 'sigmoid', 'sigmoid', 'sigmoid'}"
        
    def config_layers(self, widget):
        configDlg = ConfigLayersDialog()
        result, layers = configDlg.run()
        
        if result == gtk.RESPONSE_OK:
            self.USER_NETWORK = layers
            self.USE_DEFAULT_NET = False
           
    def get_network_config(self):
        if self.USE_DEFAULT_NET == False:
            lsizes = []
            ltypes = []
            for i in range(len(self.USER_NETWORK)):
                lsizes.append(self.USER_NETWORK[i][0])
                ltypes.append(self.USER_NETWORK[i][1])    
            sizestr = ', '.join(lsizes)
            typestr = "', '".join(ltypes)
            self.LAYER_SIZES = "[" + sizestr + "]"
            self.LAYER_TYPES = "{'" + typestr + "'}"

    def set_train_ultrasound(self, widget):
        """Called when user clicks the train ultrasound toggle button
           in the main window. Sets parameter TRAIN_ULTRASOUND, which 
           determines whether the ultrasound images will be used during
           training.
        """
        if self.TRAIN_ULTRASOUND == False:
            self.TRAIN_ULTRASOUND = True
        else: 
            self.TRAIN_ULTRASOUND = False
            
    def set_train_contours(self, widget):
        """Similar to set_train_ultrasound, except it determines whether
           contour data will be used in training.
        """
        if self.TRAIN_CONTOURS == False:
            self.TRAIN_CONTOURS = True
        else: 
            self.TRAIN_CONTOURS = False
        
    def set_train_audio(self, widget):
        """Not implemented yet"""
        pass

    def set_train_velum(self, widget):
        """Not implemented yet"""
        pass
   
    def set_train_glottis(self, widget):
        """Not implemented yet"""
        pass
        
    def set_train_lips(self, widget):
        """Not implemented yet"""
        pass

    def set_train_transcription(self, widget):
        """Not implemented yet"""
        pass
        
    def set_test_ultrasound(self, widget):
        """Called when user clicks the test ultrasound toggle button
           in the main window. Sets parameter TEST_ULTRASOUND, which 
           determines whether the ultrasound images will be used at runtime
        """
        if self.TEST_ULTRASOUND == False:
            self.TEST_ULTRASOUND = True
        else: 
            self.TEST_ULTRASOUND = False

    def set_test_contours(self, widget):
        """Similar to set_train_ultrasound, except it determines whether
           contour data will be used at runtime.
        """
        if self.TEST_CONTOURS == False:
            self.TEST_CONTOURS = True
        else: 
            self.TEST_CONTOURS = False

    def set_test_audio(self, widget):
        """Not implemented yet"""
        pass

    def set_test_velum(self, widget):
        """Not implemented yet"""
        pass

    def set_test_glottis(self, widget):
        """Not implemented yet"""
        pass
        
    def set_test_lips(self, widget):
        """Not implemented yet"""
        pass

    def set_test_transcription(self, widget):
        """Not implemented yet"""
        pass


    def train(self, widget):
        """This calls the matlab scripts and passes the parameters to them"""
        args = self.parse_args()
        #argstr = "cd ~/autotracer/trunk/TrainNetwork/; TrainNetwork" + args + "; quit()"
        argstr = "TrainNetwork" + args + "; quit()"
        print argstr
        cmd = ['matlab', '-nodesktop', '-nosplash', '-r', argstr]
        self.ctv.run(cmd)
        
        
    def cancel_training(self, widget):
        """Stops the matlab training scripts"""
        self.ctv.cancel()
        
    def parse_args(self):
        """This function is run when the user presses 'Go', and figures out all the settings from the buttons.
        For now we'll ignore all the training and test params, except ultrasound and contours
        function will need the following input args:
        (bool train_ultrasound, bool train_contours, bool test_ultrasound, bool test_contours, 
         bool practice_run, int max_images, bool use_crossval, int nfolds, 
         str network_sizes, str network_types, str data_dir, str subject_nums)"""
        args = []
        args.append(str(self.TRAIN_ULTRASOUND).lower())
        args.append(str(self.TRAIN_CONTOURS).lower())
        args.append(str(self.TEST_ULTRASOUND).lower())
        args.append(str(self.TEST_CONTOURS).lower())

        args.append(str(self.PRACTICE_RUN).lower())
        if self.PRACTICE_RUN == True:
            args.append(self.get_max_images())
        else:
            args.append('Inf')
        args.append(str(self.USE_CROSSVAL).lower())
        args.append(self.get_nFolds())

        self.get_network_config()
        args.append("'" + self.LAYER_SIZES + "'")
        args.append(self.LAYER_TYPES)
        
        args.append("'" + self.DATA_DIR + "'")
        args.append(self.SUBJECT_NUMS)
        
        self.pathtofiles = self.DATA_DIR + "/Subject" + self.SUBJECT_NUMS[1] + '/'
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
        args.append([top, bottom, left, right])

        argstrlist = []
        for i in range(len(args)):
            print args[i]
            argstrlist.append(str(args[i]))
            
        argstr = "(" + ", ".join(argstrlist) + ")"
        return argstr
        
        
    def add_data(self, widget):
        fc = gtk.FileChooserDialog(title='Select Data Folders...', parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
        fc.set_current_folder(g_directory)
        fc.set_default_response(gtk.RESPONSE_OK)
        fc.set_select_multiple(True)
        response = fc.run()
        if response == gtk.RESPONSE_OK:
            dirs = fc.get_filenames()
            g_directory = fc.get_current_folder()
            self.getSubjectNums(dirs)
        fc.destroy()
        
    def getSubjectNums(self, dirlist):
        subjectNums = []
        for i in range(len(dirlist)):
            s = dirlist[i].split('/Subject')
            subjectNums.append(s[1])

        self.SUBJECT_NUMS = "[" + ", ".join(subjectNums) + "]"                   
        self.DATA_DIR = s[0]            
            
        
class CommandTextView(gtk.TextView):
    """TextView that reads stdout of a subprocess - takes a unix command as input"""
    def __init__(self):
        super(CommandTextView, self).__init__()

    def run(self, command):
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.write_to_buffer)

    def write_to_buffer(self, fd, condition):
        if condition == gobject.IO_IN:
            char = fd.read(1)
            buf = self.get_buffer()
            buf.insert_at_cursor(char)
            return True
        else:
            return False
            
    def cancel(self):
        self.proc.send_signal(15)
                
class ConfigLayersDialog:
    """This class is used to get sizes and types of layers of the network"""
    
    def __init__(self):
        self.gladefile = "TrainNetwork.glade"
        
    def run(self):
        self.wTree = gtk.glade.XML(self.gladefile, "ConfigureNetwork")
        dic = {"on_tbAddLayer_clicked" : self.onAddLayer }
        self.wTree.signal_autoconnect(dic)
        
        self.dlg = self.wTree.get_widget("ConfigureNetwork")
        
        self.tView = self.wTree.get_widget("treeview1")
        self.cSize = 0
        self.cType = 1
        self.sSize = "Size"
        self.sType = "Type"
        self.AddColumn(self.sSize, self.cSize)
        self.AddColumn(self.sType, self.cType)

        self.LayerList = gtk.ListStore(str, str)
        self.tView.set_model(self.LayerList)
        
        #This will be the returned data
        self.layers = []
        
        self.result = self.dlg.run()
        
        self.dlg.destroy()
        
        return self.result, self.layers
                
    def AddColumn(self, title, columnId):
        column = gtk.TreeViewColumn(title, gtk.CellRendererText(), text=columnId)
        column.set_resizable(True)
        column.set_sort_column_id(columnId)
        self.tView.append_column(column)
        
        
    def onAddLayer(self, widget):
        layerDlg = layerDialog()
        result, newLayer = layerDlg.run()
        
        if (result == gtk.RESPONSE_OK):
            self.LayerList.append(newLayer.getList())
            self.layers.append(newLayer.getList())
            
class layerDialog:
    """This class shows the dialog for adding layers to the network"""
    
    def __init__(self, size="", ltype=""):
        self.gladefile = "TrainNetwork.glade"
        self.layer = Layer(size, ltype)
        
    def run(self):
        self.wTree = gtk.glade.XML(self.gladefile, "AddLayer")
        self.dlg = self.wTree.get_widget("AddLayer")
        self.enSize = self.wTree.get_widget("enSize")
        self.enSize.set_text(self.layer.size)
        
        self.enTypeCB = self.wTree.get_widget("enTypeCB")
        self.result = self.dlg.run()
        self.layer.size = self.enSize.get_text()
        self.layer.ltype = self.enTypeCB.get_active_text()
        
        self.dlg.destroy()
        
        return self.result, self.layer
        
class Layer:
    """This class holds the layer information"""
    
    def __init__(self, size="", ltype=""):
        self.size = size
        self.ltype = ltype
       
    def getList(self):
        return [self.size, self.ltype]
       
if __name__ == "__main__":
    TrainNetwork()
    gtk.main()
