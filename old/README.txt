LabTools version 0.01_Feb21_2011
Copyright (C) 2011 Jeff Berry jjberry@email.arizona.edu

This program is free software; you can modify it 
under the terms of the CRAPL License as published 
by Matthew Might at
http://matt.might.net/articles/crapl/

==================================================
INSTALLATION
This code depends on a lot of other software, both
open source and proprietary.
The software has been tested only on Mac OS X, 
although all software used here is available on Windows 
and Linux, but may be more difficult to install, 
especially for Windows.

1. Matlab
The neural network code is primarily written in Matlab, 
so you will need to have that installed. Matlab must be 
callable from the command line, as the python interfaces 
open Matlab as a subprocess. To test whether you have 
Matlab correctly installed, type the following in a 
terminal window:

matlab -nodesktop

If Matlab starts up correctly then you can proceed.

2. Macports
Most of the other software can be installed on Mac OS X
via Macports http://www.macports.org/ 
Once Macports is installed, make sure it is updated:

sudo port selfupdate
sudo port upgrade outdated

Be sure to make sure that /opt/local/bin is on your PATH.
This can be done by adding the following to ~/.bash_profile

export PATH=/opt/local/bin:$PATH

The necessary libraries can be installed with the following 
commands, which will take several hours (or more) to compile.

sudo port install python26 python_select
sudo python_select python26
sudo port install py26-gtk
sudo port install py26-matplotlib +gtk2 +latex
sudo port install opencv +python26
sudo port install py26-gnome py26-pil py26-scipy glade3 ImageMagick R

Note: the last command will install a new version of R in 
/opt/local/bin/R
If you want to use this as your default R installation, 
you will need to add an alias to ~/.bash_profile

alias R=/opt/local/bin/R

For some reason, if you have a previous installation, the
new R will be ignored without that alias. You will also
need to install the assist package in R, which can be done
by starting R and typing

install.packages('assist')

If you don't want to use the Macports R, then leave it off 
of the last port command.

3. Praat
You will also need Praat to be installed in the normal place.
http://www.fon.hum.uva.nl/praat/
Several system calls are made to Praat using:

/Applications/Praat.app/Contents/MacOS/Praat

so if Praat is located somewhere else, you will need to change 
those lines.

4. peterotron
You will need to compile the peterotron program, 
which is used for head correction.

gcc peterotron.c -lm -o peterotron

==================================================
The following files should be included in this version.

AnalysisWindow.py
AutoTrace.py
AutoTracer.m
CRAPL-LICENSE.txt
Compare.glade
CompareContours.py
FileRename.glade
FileRename.py
LabelWindow.py
LinguaView.py
LinguaViewer.glade
PGLite.py
README.txt
SelectROI.py
TrainNetwork.glade
TrainNetwork.m
TrainNetwork.py
addheadcorr.py
cleanspec.sh
configdir.py
fixImages.py
format4R.py
image_diversity.py
makeSpec.praat
neutralContour.py
neutralContourSimple.py
peterotron.c
playSound.praat
roi.glade
settings.txt
ssanova.R
NeuralNets/
	RidgeLastLayer.m
	SimpleSoftmaxNet.m
	backprop.m
	backprop_gradient.m
	backprop_nca_gradient.m
	cleanContours.m
	combineUltrasoundAndContourImages.m
	getBinSmoothHandle.m
	getPRMLdata.m
	get_recon_error.m
	lbfgsNN.m
	loadContours.m
	makeContourImages.m
	minimize.m
	nnonlinnca.m
	normalizedata.m
	normed_run_through_network.m
	runThroughKNetworks.m
	run_through_network.m
	sampleContFiles.m
	splitDataAndNet.m
	testnet.m
	testnormalize.m
	trainRBM.m
	train_deep_network.m
	train_rbm.m
savefiles/
	watchdog.py
	

==================================================
USAGE
See the documentation.

How to Change which channel of audio is displayed in LinguaView.py:
change line 7 of makeSpec.praat to 'Extract right channel'
change line 132 of neutralContour.py to 'chan = snd[:,1]'

