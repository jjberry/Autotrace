#!/usr/bin/env python

'''
configdir.py
Written by Jeff Berry on Jan 11 2011
Modified by Gus Hahn-Powell on March 6 2014 & April 29 2014

purpose:
	This script arranges training data into the directory
	structure that TrainNetwork.py expects.

usage:
	python configdir.py

	This script now launches a GUI that will allow the user to select a directory
	containing .jpg/.png and corresponding .traced.txt files,
	as well as ROI_config.txt (optional).

	The contents of this directory will be organized into the following format:

	Subject1
	--> TongueContours.csv
	--> IMAGES
		 --> jpg and/or png files

	--> traces
		 --> traced.txt files

	--> ROI_config.txt (if present)

--------------------------------------------------
Modified by Jeff Berry on Feb 19 2011
reason:
	Added support for ROI_config.txt
'''

import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
import os, subprocess, re, sys
from PIL import Image #for grayscale image preparation

image_extension_pattern = re.compile("\.(jpg|png)$", re.IGNORECASE)


class TkFileDialogExample(Tkinter.Frame):

	def __init__(self, root):

		Tkinter.Frame.__init__(self, root)

		# text field
		text = Tkinter.Text(self, width=30, height=10, wrap="word", padx=10, pady=10, font='helvetica 18', background='white smoke')
		text.insert('1.0', "Please select a directory to prepare for AutoTrace training.")
		text.pack()

		# button optoins
		button_opt = {'fill': Tkconstants.BOTH, 'padx': 10, 'pady': 10}

		# buttons
		Tkinter.Button(self, text='Select Directory', command=self.askdirectory).pack(**button_opt)
		Tkinter.Button(self, text="Quit", command=sys.exit).pack(**button_opt)

		# options for opening directory
		self.dir_opt = options = {}
		options['initialdir'] = os.path.expanduser("~")
		options['mustexist'] = True
		options['parent'] = root
		options['title'] = 'Configure Directory'

	def askdirectory(self):

		"""Returns a selected directory name."""

		self.dir = tkFileDialog.askdirectory(**self.dir_opt)
		# move to specified directory
		os.chdir(self.dir)
		self.configdir()


	def formatAutoTrace(self):
			filename = 'Subject1/TongueContours.csv'
			with open(filename, 'w') as o:
				o.write("Filename\tRaw.R1.X\tRaw.R1.Y\tRaw.R2.X\tRaw.R2.Y\tRaw.R3.X\tRaw.R3.Y\tRaw.R4.X\tRaw.R4.Y\tRaw.R5.X\tRaw.R5.Y\tRaw.R6.X\tRaw.R6.Y\tRaw.R7.X\tRaw.R7.Y\tRaw.R8.X\tRaw.R8.Y\tRaw.R9.X\tRaw.R9.Y\tRaw.R10.X\tRaw.R10.Y\tRaw.R11.X\tRaw.R11.Y\tRaw.R12.X\tRaw.R12.Y\tRaw.R13.X\tRaw.R13.Y\tRaw.R14.X\tRaw.R14.Y\tRaw.R15.X\tRaw.R15.Y\tRaw.R16.X\tRaw.R16.Y\tRaw.R17.X\tRaw.R17.Y\tRaw.R18.X\tRaw.R18.Y\tRaw.R19.X\tRaw.R19.Y\tRaw.R20.X\tRaw.R20.Y\tRaw.R21.X\tRaw.R21.Y\tRaw.R22.X\tRaw.R22.Y\tRaw.R23.X\tRaw.R23.Y\tRaw.R24.X\tRaw.R24.Y\tRaw.R25.X\tRaw.R25.Y\tRaw.R26.X\tRaw.R26.Y\tRaw.R27.X\tRaw.R27.Y\tRaw.R28.X\tRaw.R28.Y\tRaw.R29.X\tRaw.R29.Y\tRaw.R30.X\tRaw.R30.Y\tRaw.R31.X\tRaw.R31.Y\tRaw.R32.X\tRaw.R32.Y\tUL.x\tUL.y\tUR.x\tUR.y\tLL.x\tLL.y\tLR.x\tLR.y\tAux1.x\tAux1.y\tAux2.x\tAux2.y\tAux3.x\tAux3.y\tAux4.x\tAux4.y\tAux5.x\tAux5.y\tAux6.x\tAux6.y\tAux7.x\tAux7.y\tAux8.x\tAux8.y\tAux9.x\tAux9.y\tAux10.x\tAux10.y\n")

				fnamesl = sorted(os.listdir('.'))
				fnames = []
				for i in fnamesl:
						if '.traced.txt' in i:
								fnames.append(i)
				warnings = 0
				for i in fnames:
						f = open(i, 'r').readlines()
						if (len(f) != 32):
								print '\033[91m' + 'Warning: ' + i + ' does not have 32 lines\n\tThis will cause an error during training' + '\033[0m'
								warnings += 1
						nums = []
						for j in range(len(f)):
								x = f[j][:-1].split('\t')
								nums.append(int(round(float(x[1]))))
								nums.append(int(round(float(x[2]))))

						for k in range(8):
								nums.append(-1)

						for l in range(20):
								nums.append(-1)
						name = '.'.join(i.split('.')[0:2])
						#o.write('%s' % i[:-11])
						o.write('%s' % name)
						for k in nums:
							o.write('\t%s' % k)
						o.write('\n')


			if warnings > 0:
					print "There were %d warnings" % warnings

	def grayscale_handling(self):
		"""
		This method ensures that grayscaled images are handled properly by AutoTrace
		"""
		path = os.path.join(os.getcwd(), 'Subject1', 'IMAGES')
		for f in os.listdir(path):
			# bandaid for Matlab stuff
			# even if the image is grayscale, "pretend" it's actually RGB, so that Matlab handles it properly...
			if f.endswith('jpg') or f.endswith('JPG'):
				source_name = os.path.join(path, f)
				im = Image.open(source_name).convert("RGB")
				im.save(source_name)

	def configdir(self):
			if not os.path.isdir('Subject1'):
					os.makedirs('Subject1/IMAGES/')
					os.mkdir('traces')

			self.formatAutoTrace()

			tracecount = 0
			jpgcount = 0
			files = sorted(os.listdir('.'))
			for i in files:
					if '.traced.txt' in i:
							cmd = ['mv', i, 'traces']
							p = subprocess.Popen(cmd)
							p.wait()
							tracecount += 1
					elif re.search(image_extension_pattern, i):
							cmd = ['mv', i, 'Subject1/IMAGES']
							p = subprocess.Popen(cmd)
							p.wait()
							jpgcount += 1
			if os.path.isfile('ROI_config.txt'):
					subprocess.Popen(['cp', 'ROI_config.txt', 'Subject1/'])
			if os.path.isfile('../ROI_config.txt'):
					subprocess.Popen(['cp', '../ROI_config.txt', 'Subject1/'])

			# handle grayscale images
			self.grayscale_handling()

			tkMessageBox.showinfo("Success", "moved {0} images and {1} traces".format(jpgcount, tracecount))
			if jpgcount != tracecount:
					print '\033[91m' + 'Warning: There is a mismatch in number of images and number of traces' + '\033[0m'

if __name__=='__main__':
	root = Tkinter.Tk()
	TkFileDialogExample(root).pack()
	root.mainloop()
