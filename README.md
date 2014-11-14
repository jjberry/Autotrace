Autotrace
=========

A collection of tools to analyze tongue surface contours in ultrasound images.

##[Matlab-version](https://github.com/jjberry/Autotrace/tree/master/matlab-version)
The older, fully-functioning AutoTrace system requires Matlab and several python dependencies related to GTK+.  Because of GTK+, this version is best run on Linux, although it can be installed on Mac OS X using MacPorts (http://www.macports.org/).



##[Matlab-free version](https://github.com/jjberry/Autotrace/tree/master/under-development) (under-development)
A Matlab-free version is currently under development.  This new version will require PyQt4 to be installed, which is available
from http://www.riverbankcomputing.com/software/pyqt/intro  
PyQt4 requires Qt to be installed which can be obtained from http://qt-project.org/

The code for training deep networks is adapted from the author's translational-DBN repository (https://github.com/jjberry/translational-DBN)
which requires gnumpy.py (http://www.cs.toronto.edu/~tijmen/gnumpy.html) to be on the system's Python `PATH`.
The use of gnumpy.py allows the network to be trained on a CUDA-capable GPU if present, using the `cudamat` library (https://code.google.com/p/cudamat/)
If no GPU is present, `gnumpy.py` will use the CPU, which requires `npmat.py` (http://www.cs.toronto.edu/~ilya/npmat.py).

The Qt-based tools are cross platform, and have been tested on Windows 7, Linux, and Mac OS X, with Qt 4.8.
