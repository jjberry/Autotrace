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


log_file = os.path.join(os.getcwd(), "tmp_log")

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
	"""
	"""
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
		self.log_file = ""

	def logger(self, message, log_file=log_file):
		"""
		logger
		"""
		with open(log_file, 'a') as lg:
			lg.write("{0}\n".format(message))

	def get_roi(self):
		"""
		Get Region of Interest (RoI) for selected images
		"""
		# get an image and open it to see the size
		img = cv.LoadImageM(self.images[0], iscolor=False)
		self.csize = shape(img)
		self.img = asarray(img)
		
		#open up the ROI_config.txt and parse
		self.logger("images_dir: {0}".format(self.images_dir))
		#see if the ROI_config.txt file exists at the specified directory...should we instead launch SelectROI.py?
		self.config = os.path.join(self.images_dir,'ROI_config.txt') if os.path.exists(os.path.join(self.images_dir,'ROI_config.txt')) else None
		self.logger("self.config: {0}".format(self.config))
		if self.config:
			self.logger("Found ROI_config.txt")
			c = open(self.config, 'r').readlines()
			self.top = int(c[1][:-1].split('\t')[1])
			self.bottom = int(c[2][:-1].split('\t')[1])
			self.left = int(c[3][:-1].split('\t')[1])
			self.right = int(c[4][:-1].split('\t')[1])
			self.logger("using ROI: [%d:%d, %d:%d]" % (self.top, self.bottom, self.left, self.right))
		else:
			self.logger("ROI_config.txt not found")
			self.top = 140 #default settings for the Sonosite Titan
			self.bottom = 320
			self.left = 250
			self.right = 580
			self.logger("using ROI: [%d:%d, %d:%d]" % (self.top, self.bottom, self.left, self.right))
		
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
		"""
		"""
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
			self.logger("{0} images found".format(len(self.images)))
			self.logger("images: {0}".format("\n".join(self.images)))
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
			self.logger("{0} traces found".format(len(self.traces)))
			self.logger("traces: {0}".format("\n".join(self.traces)))
		fc.destroy()
		self.get_tracenames()

	def openDest(self, event):
		"""
		"""
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
			self.log_file = os.path.join(self.destpath, "diversity_log")
		fc.destroy()  

	def makeDest(self):
		"""
		"""
		#TODO: add this into openDest?
		diverse_dir = os.path.join(self.destpath, "diverse")
		self.logger("images will be saved in " + diverse_dir)
		if not os.path.isdir(diverse_dir):
			os.mkdir(diverse_dir)
			self.logger("created directory" + diverse_dir)

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
					self.logger("image: {0}\ttrace: {1}".format(image_name, trace_name))
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

		#print "remaining: {0}".format(self.remaining.get_text())
		self.remaining.set_text(str(self.n - self.safe_get(self.train_most) - self.safe_get(self.train_least)))
		#make sure we don't have more batches than remaining...
		if self.safe_get(self.batches) > self.safe_get(self.remaining):
			self.batches.set_text(str(self.remaining))

	def check_remaining(self):
		"""
		"""
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
	
	def make_train_test(self, images, training_n, testing_n=None):
		"""
		takes a list of images and test and training sizes
		returns two lists of non-overlapping images  (training, testing)
		"""
		images_array = array(images)
		images_indices = arange(len(images_array))
		random.shuffle(images_indices)

		traininds = images_indices[:training_n]
		trainfiles = images_array[traininds]

		testfiles = []
		#make sure we have a test set
		if testing_n:
			testinds = images_indices[training_n:training_n+testing_n]
			testfiles = images_array[testinds]

		#return training, testing
		return list(trainfiles), list(testfiles)

	def move_files(self, images, destination, image_class="??"):
		"""
		"""
		#move our test files...
		self.logger("Moving {0} {1} files...".format(len(images), image_class))
		for image in images:
			image_name = os.path.basename(image)
			dest = os.path.join(destination, image_name)
			shutil.copy(image, dest)
			if image in self.tracenames:
				#should I average the traces instead?
				for trace in self.tracenames[image]:
					trace_name = os.path.basename(trace)
					dest = os.path.join(destination, trace_name)
					self.logger("image: {0}".format(image))
					self.logger("trace source: {0}".format(trace))
					self.logger("trace dest: {0}\n".format(dest))
					shutil.copy(trace, dest)

	def plot_diversity(self, sorted_results):
		"""
		"""
		#show rank vs. energy plot
		count = 0
		for (i,j) in sorted_results:
			count += 1
			plot.plot(count, j, 'b.')
		#add confirmation dialog that prompts for save location when ok is clicked
		#plot.savefig(os.path.join(self.destpath, 'rankVenergy.png'))
		plot.title("rank vs. energy plot for {0} images".format(count))
		plot.ylabel('Diversity score')
		plot.xlabel('Rank')
		#remove x axis ticks
		#plot.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		plot.show()

	def get_diverse(self):
		"""
		get specified diversity set and 
		then copy relevant files to specified location
		"""
		batches = self.safe_get(self.batches)

		if os.path.isdir(self.destpath):
			self.logger("calculating average image...")
			ave_img, files = self.get_average_image()
		
			self.logger("measuring distances from average...")
			results = {}
			for i in range(len(self.images)):
				img = cv.LoadImageM(self.images[i], iscolor=False)
				roi = img[self.top:self.bottom, self.left:self.right]
				roi = asarray(roi)/255.
				dif_img = abs(roi - ave_img)
				results[self.images[i]] = sum(sum(dif_img))
		
			sorted_results = sorted(results.iteritems(), key=operator.itemgetter(1), reverse=True)

			#plot rank vs diversity
			self.plot_diversity(sorted_results)

			most_diverse_n = self.safe_get(self.train_most)
			least_diverse_n = self.safe_get(self.train_least)
			
			test_most_diverse_n = self.safe_get(self.test_most)
			test_least_diverse_n = self.safe_get(self.test_least)
			
			training_most_diverse_n = most_diverse_n - test_most_diverse_n
			training_least_diverse_n = least_diverse_n - test_least_diverse_n

			test_size = test_most_diverse_n + test_least_diverse_n
			self.logger("test size: {0}".format(test_size))
			#remove test size from training size...
			train_size = most_diverse_n + least_diverse_n - test_size
			self.logger("training size: {0}".format(train_size))
			
			all_images = [image for (image, _) in sorted_results]
			most_diverse_images = []
			least_diverse_images = []

			#get n most diverse...
			if most_diverse_n > 0:
				self.logger("Selecting {0} most diverse images...".format(most_diverse_n))
				for (image, score) in sorted_results[:most_diverse_n]:
					self.logger("file: {0}\ndiversity score: {1}\n".format(image, score))
					most_diverse_images.append(image)

				#get most diverse for testing and training...
				training_most_diverse, testing_most_diverse = self.make_train_test(most_diverse_images, training_n=training_most_diverse_n, testing_n=test_most_diverse_n)
			else:
				training_most_diverse = []
				testing_most_diverse = []

			#get n least diverse...
			if least_diverse_n > 0:
				self.logger("Selecting {0} least diverse images...".format(least_diverse_n))
				#take the specified n least diverse...
				for (image, score) in sorted_results[-1*least_diverse_n:]:
					self.logger("file: {0}\ndiversity score: {1}\n".format(image, score))
					least_diverse_images.append(image)
				
				#get least diverse for testing and training...
				training_least_diverse, testing_least_diverse = self.make_train_test(least_diverse_images, training_n=training_least_diverse_n, testing_n=test_least_diverse_n)
			else:
				training_least_diverse = []
				testing_least_diverse = []
			
			#make test, training, and batch file sets...
			trainfiles = training_most_diverse + training_least_diverse
			testfiles = testing_most_diverse + testing_least_diverse

			#find remaining...
			selected = set(trainfiles + testfiles)
			remainingfiles = [image for image in all_images if image not in selected]

			#prepare directory for training files...	
			self.traindir = os.path.join(self.destpath, "train")
			if not os.path.isdir(self.traindir):
				os.mkdir(self.traindir)	
			
			#move training files (edit this)...
			self.move_files(trainfiles, destination=self.traindir, image_class="training")

			#are we generating a test set?
			if test_size > 0:
				#prepare directory for test files...
				self.testdir = os.path.join(self.destpath, "test")
				if not os.path.isdir(self.testdir):
					os.mkdir(self.testdir)

				#move our test files...
				self.move_files(testfiles, destination=self.testdir, image_class="test")

			#get remaining and make n batches...
			if batches > 0:				
				b_num = 1
				#numpy trick works here...
				for batch_files in array_split(array(remainingfiles), batches):
					#pad batch folder name with some zeros
					batch_name = "batch%03d" % (b_num)
					self.logger("files in {0}: {1}".format(batch_name, len(batch_files)))
					batch_dir = os.path.join(self.destpath, batch_name)
					if not os.path.isdir(batch_dir):
						os.mkdir(batch_dir)
					
					#move batch files
					self.move_files(batch_files, destination=batch_dir, image_class=batch_name)
					#increment batch...
					b_num+=1

			# write sorted_results to a .txt file for future reference
			# added Mar 10 2011 by Jeff Berry
			o = open(os.path.join(self.destpath, 'SortedResults.txt'), 'w')
			for (i,j) in sorted_results:
				o.write("%s\t%.4f\n" %(i, j))
			o.close()

		#move ROI file...
		roifile = os.path.join(self.images_dir, "ROI_config.txt")
		if os.path.isfile(roifile):
			self.logger("moving ROI_config.txt to {0}".format(roifile))
			shutil.copy(self.destpath, "ROI_config.txt")

	def onOK(self, event):
		"""
		"""
		if not self.destpath or not self.images or self.safe_get(self.train_most) == 0:
			#run error dialog and return...
			error_dialog = gtk.MessageDialog(parent=None, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Some of your settings are missing...")
			error_dialog.run()
			error_dialog.destroy()
			return

		self.get_roi()
		self.get_diverse()
		gtk.main_quit()
		self.logger("exiting...")
		shutil.move(log_file, self.log_file)
			

if __name__ == "__main__":
	ImageWindow()
	gtk.main()

