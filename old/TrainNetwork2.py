#!/usr/bin/env python

'''
TrainNetwork.py
Written by Jeff Berry Jul 1 2010
Revised by Gus Hahn-Powell March 8 2014

purpose:
	Train a translational Deep Belief Network for tracing. The training
	data should be arranged in a folder called Subject<N>, where N is any
	positive integer, such as Subject1. Images are located in Subject1/IMAGES/
	and should be .jpg or .png files. The traces are in Subject1/TongueContours.csv,
	which can be created using AutoTrace.py or configdir.py. Parameters 
	defining the region of interest should be listed in Subject1/ROI_config.txt,
	otherwise a default ROI will be used. The resulting tDBN will be located
	in savefiles/network<time>.mat.

usage:
	python TrainNetwork2.py
---------------------------------------------

Modified by Jeff Berry Feb 19 2011
reason:
	Updated to make use of ROI_config.txt, which should be in the same
	folder as JPG/ and TongueContours.csv
'''

import sys, os
import subprocess as sp
import re
import smtplib
try:
	import pygtk
	pygtk.require("2.0")
except:
	pass
try:
	import gtk
	import gtk.glade
except:
	sys.exit(1)

subject_number_pattern = re.compile("Subject([0-9]+)",re.IGNORECASE)

class TrainNetwork:
	"""This is the class for the main window of trainnetwork.py"""
	
	def __init__(self):
		
		#Set the Glade file
		self.gladefile = "TrainNetwork2.glade"
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
				"on_train_clicked" : self.train,
				"on_cancel_clicked" : self.cancel_training,
				"on_notify_toggled" : self.set_notify }
		self.wTree.signal_autoconnect(dic)
			   
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
		
	#Callback definitions   
	def set_defaults(self):
		self.MAX_NUM_IMAGES = 100
		self.NFOLDS = 5
		self.PRACTICE_RUN = False
		self.USE_CROSSVAL = False
		self.USE_DEFAULT_NET = True
		self.TRAIN_ULTRASOUND = True
		self.TRAIN_CONTOURS = True
		self.TRAIN_AUDIO = False
		self.TRAIN_VELUM = False
		self.TRAIN_GLOTTIS = False
		self.TRAIN_LIPS = False
		self.TRAIN_TRANSCRIPTION = False
		self.TEST_ULTRASOUND = True
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
		self.NOTIFY = False         
				 
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
		g_directory = fc.get_current_folder() if fc.get_current_folder() else os.path.expanduser("~")
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
	
	def set_notify(self, widget):
		if self.NOTIFY == False:
			self.NOTIFY = True
		else:
			self.NOTIFY = False

	def train(self, widget):
		"""This calls the matlab scripts and passes the parameters to them"""
		args = self.parse_args()
		#argstr = "cd ~/autotracer/trunk/TrainNetwork/; TrainNetwork" + args + "; quit()"
		argstr = "TrainNetwork" + args + "; quit()"
		print argstr
		cmd = ['matlab', '-nodesktop', '-nosplash', '-r', argstr]
		self.proc = sp.Popen(cmd)
		self.proc.wait()
		
		if self.NOTIFY:
			self.send_notification(argstr)        
		
	def send_notification(self, argstr):
		print "done"        
		senderentry = self.wTree.get_widget("senderentry")
		passwordentry = self.wTree.get_widget("passwordentry")
		recipiententry = self.wTree.get_widget("recipiententry")
		FROMADDR = senderentry.get_text()
		LOGIN    = FROMADDR
		PASSWORD = passwordentry.get_text()
		TOADDRS  = [recipiententry.get_text()]
		SUBJECT  = "Network finished training"

		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
			   % (FROMADDR, ", ".join(TOADDRS), SUBJECT) )
		msg += "done\r\n" + argstr

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.set_debuglevel(1)
		server.ehlo()
		server.starttls()
		server.login(LOGIN, PASSWORD)
		server.sendmail(FROMADDR, TOADDRS, msg)
		server.quit()
		
		
	def cancel_training(self, widget):
		"""Stops the matlab training scripts"""
		self.proc.send_signal(15)
		
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
		fc = gtk.FileChooserDialog(title='Select Subject<N> folders to use...', parent=None, 
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
		
		subjectNums = [re.search(subject_number_pattern, subject_folder).group(1) for subject_folder in dirlist if re.search(subject_number_pattern, subject_folder)]

		self.SUBJECT_NUMS = "[" + ", ".join(subjectNums) + "]"                   
		self.DATA_DIR = os.path.dirname(dirlist[0])        

							
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
