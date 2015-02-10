AutoTrace Walkthrough. 
===
>This manual will explain the process of how to use Autotrace to trace images, train a network, and generate traces. 

Tracing Manually
----

+ Open [Autotrace](autotrace.md) and follow the manual instructions. 
	+ If you do not already have traced data, it is recommended that you use this manual method to generate a __training set__ upon which to construct the deep belief network as explained below. 

Tracing Automatically
----

+ Before anything, your images must be in .jpg format, _not_ .png. If you have .png images, convert them using the included __png_to_jpg.py__ script, by typing `python png_to_jpg.py /path/to/png/images`. 

+ First, use [SelectROI](selectroi.md) to create a ROIconfig.txt file. Remember where you put it, we may need to move it later. 

+ Next, use [ImageDiversity](imagediversityNEW.md) to separate a training and test set. 

+ Then, use [ConfigDir](configdir.md) to arrange the training data into the proper directory structure. 
  + At this point, ROIconfig.txt should be in the /train/Subject1/ directory. If it is not, move it there. 

+ Now for the actual training. Follow the instructions in [Train Network](TrainNetwork.md). 
	+ Ensure you point TrainNetwork at train/Subject1/ _and_ train/traces using shift-click.
	+ This may take a while. Be patient. 
	+ Now you have a Deep-Belief Network tailored to your data set that will be used by Autotrace. 

+ Now you are ready to use Autotrace. Open [the manual](autotrace.md) and scroll down to the automatic tracing instructions.  


