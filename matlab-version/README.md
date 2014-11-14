#Usage

See the [documentation](https://github.com/jjberry/Autotrace/tree/master/documentation).

*How to Change which channel of audio is displayed in LinguaView.py*:  
1. change line 7 of makeSpec.praat to 'Extract right channel'
2. change line 132 of neutralContour.py to 'chan = snd[:,1]'

#Installation
This code depends on a lot of other software, both
open source and proprietary.
The software works best on Linux, but will also run on Mac OS X via macports (see the [installer script](https://github.com/jjberry/Autotrace/blob/master/installer-scripts/mac_autotrace_installer.py)).

##General requirements

1. ###Matlab
The neural network code is primarily written in Matlab,
so you will need to have that installed. Matlab must be
callable from the command line, as the python interfaces
open Matlab as a subprocess. To test whether you have
Matlab correctly installed, type the following in a
terminal window:

	`matlab -nodesktop`

2.  ###Praat  
You will also need Praat (http://www.fon.hum.uva.nl/praat/) to be installed in the normal place.

  Several system calls are made to Praat using:

  `/Applications/Praat.app/Contents/MacOS/Praat`

  If your Praat installation is located somewhere else, you will need to change
those lines.

---
##Linux (Ubuntu)

If you're using Ubuntu (or a similar distro), you can use our [installer script](https://github.com/jjberry/Autotrace/blob/master/installer-scripts/ubuntu_autotrace_installer.sh):

`./ubuntu_autotrace_installer.sh`
##Mac OS X
On Mac OS X, the dependencies are best managed through MacPorts.

####Using the installer script:

From the AutoTrace directory, run our installer script from the command line by typing:

  `python mac_autotrace_installer.py`


####Manually

Homebrew currently doesn't have support for pygtk and libgnomecanvas.  For this reason, we recommend you use MacPorts (http://www.macports.org/).
Once Macports is installed, make sure it is updated:

`sudo port selfupdate`  
`sudo port upgrade outdated`

Be sure to make sure that `/opt/local/bin` is on your `PATH`.
This can be done by adding the following to `~/.bash_profile`:

`export PATH=/opt/local/bin:$PATH`

The necessary libraries can be installed with the following
commands, which will take several hours to compile.

`sudo port install python27 python_select`  
`sudo python_select python27`  
`sudo port install py27-gtk`  
`sudo port install py27-matplotlib +gtk2 +latex`  
`sudo port install opencv +python27`
`sudo port install py27-gnome py27-pil py27-scipy glade3 ImageMagick R`

Note: the last command will install a new version of `R` in
`/opt/local/bin/R`
If you want to use this as your default R installation,
you will need to add an alias to `~/.bash_profile`:

`alias R=/opt/local/bin/R`

For some reason, if you have a previous installation, the
new `R` will be ignored without that alias. You will also
need to install the assist package in `R`, which can be done
by starting `R` and typing

`install.packages('assist')`

If you don't want to use the MacPorts `R`, then leave it off
of the last port command.

___
The following files should be included in this version:

`AnalysisWindow.py`  
`AutoTrace.py`  
`AutoTracer.m`  
`Compare.glade`  
`CompareContours.py`  
`FileRename.glade`  
`FileRename.py`  
`LabelWindow.py`  
`LinguaView.py`  
`LinguaViewer.glade`  
`PGLite.py`  
`README.md`  
`SelectROI.py`  
`TrainNetwork.glade`  
`TrainNetwork.m`  
`TrainNetwork.py`  
`addheadcorr.py`  
`cleanspec.sh`  
`configdir.py`  
`fixImages.py`  
`format4R.py`  
`image_diversity.py`  
`image_diversityNEW.py`  
`makeSpec.praat`  
`neutralContour.py`  
`neutralContourSimple.py`  
`playSound.praat`  
`roi.glade`  
`settings.txt`  
`ssanova.R`  
__NeuralNets/__  
  `RidgeLastLayer.m`  
	`SimpleSoftmaxNet.m`  
	`backprop.m`  
	`backprop_gradient.m`  
	`backprop_nca_gradient.m`  
	`cleanContours.m`  
	`combineUltrasoundAndContourImages.m`  
	`getBinSmoothHandle.m`  
	`getPRMLdata.m`  
	`get_recon_error.m`  
	`lbfgsNN.m`  
	`loadContours.m`  
	`makeContourImages.m`  
	`minimize.m`  
	`nnonlinnca.m`  
	`normalizedata.m`  
	`normed_run_through_network.m`  
	`runThroughKNetworks.m`  
	`run_through_network.m`  
	`sampleContFiles.m`  
	`splitDataAndNet.m`  
	`testnet.m`  
	`testnormalize.m`  
	`trainRBM.m`  
	`train_deep_network.m`  
	`train_rbm.m`  
__savefiles/__  
	`watchdog.py`  
