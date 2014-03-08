#!/usr/bin/env python

"""
image_diversityNEW.py
Rewritten by Gus Hahn-Powell on March 7 2014
based on ~2010 code by Jeff Berry

purpose:
	This script measures the distance from average for each image in the
	input set, and copies the specified number of highest scoring images
	to a new folder called 'diverse'. If ROI_config.txt is present in the 
	same folder as the input images, the ROI in that file will be used to 
	do the measurement. If not present, it will use a hard-coded default ROI.

usage:
	python image_diversity.py			
"""

import cv
import re
import shutil
import os, sys
import operator
from numpy import *
from collections import defaultdict
import subprocess as sp
import multiprocessing as mp
import matplotlib.pyplot as plot
import gtk
import gtk.glade



image_extension_pattern = re.compile("(\.(png|jpg)$)", re.IGNORECASE)

'''
#change this to make use of multiprocessing.pool?
class CopyThread(multiprocessing.Process):        
	def run(self):
		flag = 'ok'
		while (flag != 'stop'):
			cmd = CopyQueue.get()
			if cmd == None:
				flag = 'stop'
			else:
				#print ' '.join(cmd)
				p = sp.Popen(cmd)
				p.wait()
				FinishQueue.put(cmd)
		#print "CopyThread stopped"
'''

class ImageWindow:
	'''This file renamer expects the format of the source files to be <name>_<frame>.jpg
		<name> can be a combination of letters and numbers, and <frame> is numbers.
		The program will split on the underscore, so if filenames are not in this format
		the behavior will be unpredictable.
	'''
		
	

class ImageWindow:
	def __init__(self):
		gladefile = "ImageDiversity.glade"
		self.wTree = gtk.glade.XML(gladefile, "window1")
		self.win = self.wTree.get_widget("window1")
		self.win.set_title("Image Diversity")
		
		dic = { "on_window1_destroy" : gtk.main_quit,
				"on_open1_clicked" : self.openImages,
				"on_open2_clicked" : self.openDest,
				"on_ok_clicked" : self.onOK}
		self.wTree.signal_autoconnect(dic)
	
		self.srcfileentry = self.wTree.get_widget("srcfileentry")
		self.dstfileentry = self.wTree.get_widget("dstfileentry")
		#initialized to None...
		self.destpath = None
		
		self.train_most = self.wTree.get_widget("train_most") #Select N images
		self.train_least = self.wTree.get_widget("train_least") #Select n test?
		
		self.test_most = self.wTree.get_widget("test_most")
		self.test_least = self.wTree.get_widget("test_least")

		self.remaining = self.wTree.get_widget("remaining")
		self.batches = self.wTree.get_widget("batches")
		#assign 0 if not coercible to type int...
		self.safe_set_all()

		self.train_most.connect("changed", self.update_remaining)
		self.train_least.connect("changed", self.update_remaining)
		self.test_most.connect("changed", self.update_remaining)
		self.test_least.connect("changed", self.update_remaining)
		self.batches.connect("changed", self.update_remaining)

		self.images = []
		self.traces = []

		self.images_dir = None
		self.traces_dir = None

		self.n = len(self.images)
		self.remaining.set_text(str(self.n))
		self.update_remaining()
	
	def get_roi(self):
		"""
		Get Region of Interest (RoI) for selected images
		"""
		# get an image and open it to see the size
		img = cv.LoadImageM(self.images[0], iscolor=False)
		self.csize = shape(img)
		self.img = asarray(img)
		
		#open up the ROI_config.txt and parse
		print "images_dir: {0}".format(self.images_dir)
		#see if the ROI_config.txt file exists at the specified directory...should we instead launch SelectROI.py?
		self.config = os.path.join(self.images_dir,'ROI_config.txt') if os.path.exists(os.path.join(self.images_dir,'ROI_config.txt')) else None
		print "self.config: {0}".format(self.config)
		if self.config:
			print "Found ROI_config.txt"
			c = open(self.config, 'r').readlines()
			self.top = int(c[1][:-1].split('\t')[1])
			self.bottom = int(c[2][:-1].split('\t')[1])
			self.left = int(c[3][:-1].split('\t')[1])
			self.right = int(c[4][:-1].split('\t')[1])
			print "using ROI: [%d:%d, %d:%d]" % (self.top, self.bottom, self.left, self.right)
		else:
			print "ROI_config.txt not found"
			self.top = 140 #default settings for the Sonosite Titan
			self.bottom = 320
			self.left = 250
			self.right = 580
			print "using ROI: [%d:%d, %d:%d]" % (self.top, self.bottom, self.left, self.right)
		
		roi = img[self.top:self.bottom, self.left:self.right]
		self.roisize = shape(roi)
		
	def safe_set(self, entry, value=""):
		"""
		Make sure entered text is coercible to type int
		"""
		try:
			int(entry.get_text())
		except:
			entry.set_text(value)		

	def safe_set_all(self, value=""):
		entries = [self.train_most, self.train_least, self.test_most, self.test_least, self.remaining, self.batches]
		for entry in entries:
			try:
				int(entry.get_text())
			except:
				entry.set_text(value)

	def safe_get(self, entry):
		"""
		Safely return an int (default is 0)
		from a specified entry
		"""
		try:
			return int(entry.get_text())
		except:
			return 0

	def openImages(self, event):
		"""
		Allows user to select multiple images (jpg or png)
		"""
		fc = gtk.FileChooserDialog(title='Select Image Files', parent=None, 
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
			self.images_dir = fc.get_current_folder() #set this to an attribute?
			self.images = [os.path.join(self.images_dir, f) for f in fc.get_filenames() if re.search(image_extension_pattern, f)]
			print "{0} images found".format(len(self.images))
			print "images: {0}".format("\n".join(self.images))
			self.n = len(self.images)
			self.update_remaining()
			self.srcfileentry.set_text(self.images_dir)
		fc.destroy()
		self.get_roi()
		self.openTraces()

	def openTraces(self):
		"""
		Allows user to select multiple trace files (traced.txt)
		"""
		fc = gtk.FileChooserDialog(title='Select Trace Files', parent=None, 
			action=gtk.FILE_CHOOSER_ACTION_OPEN, 
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		g_directory = fc.get_current_folder() if fc.get_current_folder() else self.images_dir
		fc.set_current_folder(g_directory)
		fc.set_default_response(gtk.RESPONSE_OK)
		fc.set_select_multiple(True)
		ffilter = gtk.FileFilter()
		ffilter.set_name('Trace Files')
		ffilter.add_pattern('*.traced.txt')
		fc.add_filter(ffilter)
		response = fc.run()
		if response == gtk.RESPONSE_OK:
			self.traces_dir = fc.get_current_folder() #set this to an attribute?
			#should probably filter traces here (make sure images and traces match)
			self.traces = [os.path.join(self.images_dir, f) for f in fc.get_filenames() if "traced.txt" in f]
			print "{0} traces found".format(len(self.traces))
			print "traces: {0}".format("\n".join(self.traces))
		fc.destroy()
		self.get_tracenames()

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
			self.destpath = fc.get_current_folder()
			self.dstfileentry.set_text(self.destpath)
		fc.destroy()  

	def makeDest(self):
		#TODO: add this into openDest?
		diverse_dir = os.path.join(self.destpath, "diverse")
		print "images will be saved in", diverse_dir
		if not os.path.isdir(diverse_dir):
			os.mkdir(diverse_dir)
			print "created directory", diverse_dir

	def get_tracenames(self):
		"""
		This method will look for existing trace files and create a dictionary to corresponding
		image files. It will only work if all image files are in the same directory
		"""
		#3/8/2014 (Gus): Changed to support multiple corresponding traces...
		self.tracenames = defaultdict(list)
		for image in self.images:
			#get image name...
			image_name = os.path.basename(image)
			for trace in self.traces:
				#get trace name...
				trace_name = os.path.basename(trace)
				if image_name in trace_name:
					print "image: {0}\ttrace: {1}".format(image_name, trace_name)
					self.tracenames[image].append(trace)

	def update_remaining(self, *args):
		"""
		update the number of images available
		for training and test sets, given user's
		input
		"""
		self.safe_set_all()

		#need to safely get a value or assign zero if nothing
		self.check_remaining()

		print "remaining: {0}".format(self.remaining.get_text())
		self.remaining.set_text(str(self.n - self.safe_get(self.train_most) - self.safe_get(self.train_least)))
		#make sure we don't have more batches than remaining...
		if self.safe_get(self.batches) > self.safe_get(self.remaining):
			self.batches.set_text(str(self.remaining))

	def check_remaining(self):
		#test values come out of training numbers, not overall pool
		#rest test_most if value exceeds possible
		self.safe_set_all()

		if self.safe_get(self.test_most) > self.safe_get(self.train_most):
			self.test_most.set_text("")
		if self.safe_get(self.test_least) > self.safe_get(self.train_least):
			self.test_least.set_text("")

		#did we try to pick too many items?
		if self.safe_get(self.train_most) + self.safe_get(self.train_least) > self.n:
			self.train_most.set_text("")
			self.train_least.set_text("")

	def get_average_image(self):
		"""
		creates an average image from 
		a set of images and a corresponding RoI
		"""
		files = self.images        
		ave_img = zeros(self.roisize)
		for i in range(len(files)):
			img = cv.LoadImageM(files[i], iscolor=False)
			roi = img[self.top:self.bottom, self.left:self.right]
			roi = asarray(roi)/255.
			ave_img += roi
		ave_img /= len(files)    
	
		return ave_img, files
	
	def get_diverse(self):
		"""
		gets the n most diverse images from the data 
		set and copies them into path_to_save
		"""
		batches = self.safe_get(self.batches)

		if os.path.isdir(self.destpath):
			print "calculating average image..."
			ave_img, files = self.get_average_image()
		
			print "measuring distances from average..."
			results = {}
			for i in range(len(self.images)):
				img = cv.LoadImageM(self.images[i], iscolor=False)
				roi = img[self.top:self.bottom, self.left:self.right]
				roi = asarray(roi)/255.
				dif_img = abs(roi - ave_img)
				results[self.images[i]] = sum(sum(dif_img))
		
			sorted_results = sorted(results.iteritems(), key=operator.itemgetter(1), reverse=True)

			#show rank vs. energy plot
			count = 1
			for (i,j) in sorted_results:
				plot.plot(count, j, 'b.')
				count += 1
			#add confirmation dialog that prompts for save location when ok is clicked
			#plot.savefig(os.path.join(self.destpath, 'rankVenergy.png'))
			plot.title("rank vs. energy plot for {0} images".format(count))
			plot.ylabel('Diversity score')
			plot.xlabel('Rank')
			#remove x axis ticks
			#plot.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
			plot.show()
			
			filenames = []
			for (i,j) in sorted_results:
				filenames.append(i)

			most_diverse = self.safe_get(self.train_most)
			least_diverse = self.safe_get(self.train_least)
			
			test_least_diverse = self.safe_get(self.test_least)
			test_most_diverse = self.safe_get(self.test_most)
			
			test_size = test_least_diverse + test_most_diverse
			#remove test size from training size...
			train_size = most_diverse + least_diverse - test_size
			
			#do we want any least diverse?
			if least_diverse > 0:
				#take the specified n least diverse...
				for (i,j) in sorted_results[-1*least_diverse:]:
					filenames.append(i)
			

			filenames = array(filenames) 
			inds = arange(len(filenames))  
			random.shuffle(inds)

			traininds = inds[:train_size]
			trainfiles = filenames[traininds] 
			
			#are we generating a test set?
			if test_size > 0:
				#prepare directory for test files...
				self.testdir = os.path.join(self.destpath, "test")
				if not os.path.isdir(self.testdir):
					os.mkdir(self.testdir)
				
				#figure out which files will be assigned to test...
				testinds = inds[train_size:train_size+test_size]
				testfiles = filenames[testinds]

				remaininginds =inds[train_size+test_size:]
				remainingfiles = filenames[remaininginds]

				#NOTE: this should be a method...
				#move our test files...
				for image in testfiles:
					print "Moving test files..."
					image_name = os.path.basename(image)
					dest = os.path.join(self.testdir, image_name)
					shutil.copy(image, dest)
					count += 1
					if image in self.tracenames:
						#should I average the traces instead?
						for trace in self.tracenames[image]:
							trace_name = os.path.basename(trace)
							dest = os.path.join(self.testdir, trace_name)
							print "image: {0}".format(image)
							print "trace source: {0}".format(trace)
							print "trace dest: {0}\n".format(dest)
							shutil.copy(trace, dest)
							count += 1

			
			#NOTE: this should be a method...
			#prepare directory for training files...	
			self.traindir = os.path.join(self.destpath, "train")
			if not os.path.isdir(self.traindir):
				os.mkdir(self.traindir)	
			
			#move training files (edit this)...	
			for image in trainfiles:
				print "Moving training files..."
				image_name = os.path.basename(image)
				dest = os.path.join(self.traindir, image_name)
				shutil.copy(image, dest)
				count += 1
				if image in self.tracenames:
					for trace in self.tracenames[image]:
						trace_name = os.path.basename(trace)
						dest = os.path.join(self.traindir, trace_name)
						print "image: {0}".format(image)
						print "trace source: {0}".format(trace)
						print "trace dest: {0}\n".format(dest)
						shutil.copy(trace, dest)
						count += 1

			if batches > 0:				
				b_num = 1
				#numpy trick works here...
				for batch_files in array_split(array(remainingfiles), batches):
					print "files in batch set: {0}".format(len(batch_files))
					#pad batch folder name with some zeros
					batch_dir = "batch%03d" % (b_num)
					batch_dir = os.path.join(self.destpath, batch_dir)
					if not os.path.isdir(batch_dir):
						os.mkdir(batch_dir)
					
					#NOTE: this should be a method...
					for image in batch_files:
						print "Moving batch files..."
						image_name = os.path.basename(image)
						dest = os.path.join(batch_dir, image_name)
						shutil.copy(image, dest)
						count += 1
						if image in self.tracenames:
							for trace in self.tracenames[image]:
								trace_name = os.path.basename(trace)
								dest = os.path.join(batch_dir, trace_name)
								print "image: {0}".format(image)
								print "trace source: {0}".format(trace)
								print "trace dest: {0}\n".format(dest)
								shutil.copy(trace, dest)
								count += 1
					b_num+=1

			# write sorted_results to a .txt file for future reference
			# added Mar 10 2011 by Jeff Berry
			o = open(os.path.join(self.destpath, 'SortedResults.txt'), 'w')
			for (i,j) in sorted_results:
				o.write("%s\t%.4f\n" %(i, j))
			o.close()
 
	
		print "done"

		#move ROI file...
		roifile = os.path.join(self.images_dir, "ROI_config.txt")
		if os.path.isfile(roifile):
			shutil.copy(self.destpath, "ROI_config.txt")
 

	def onOK(self, event):
		#make sure everything seems alright...
		if not self.destpath or not self.images or self.safe_get(self.train_most) == 0:
			#run error dialog and return...
			error_dialog = gtk.MessageDialog(parent=None, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Some of your settings are missing...")
			error_dialog.run()
			error_dialog.destroy()
			return

		self.get_roi()
		self.get_diverse()
		gtk.main_quit()
			
if __name__ == "__main__":
	ImageWindow()
	gtk.main()
