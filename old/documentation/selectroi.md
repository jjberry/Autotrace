Select ROI Manual
===
>This script is designed to help the user select a region of interest
	to use with the set of images selected by the user. The boundaries
	can be set either by clicking and dragging, or with the text entry 
	boxes. When this script is run, it will look for a config file called
	ROI_config.txt that specifies the region of interest. If no such file
	exists, it will be created when the user presses 'Save'. Saving will
	overwrite any previous information in ROI_config.txt.
	ROI_config.txt will be used by other scripts, such as image_diversity.py, 
	Autotrace.py, and TrainNetwork.py.
	
Usage
---
+ Open [SelectROI.py](../SelectROI.py)
+ The terminal will open followed by an __Open Image Files__ screen.
![Image1SR](images/Image1SR.png)
+ Select the images you would like to average and click __open__
