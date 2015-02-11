Common Errors
=====
> This document contains solutions to problems that show up often when using Autotrace.
> Will be updated as new errors are reported or discovered.

Matlab ceases and returns errors during __Train Network__. 
--

+ Double check that ROIConfig.txt is in the __train/Subject1/__ directory. 
+ Try again, making sure to select both __train/Subject1/__ and __train/traces__. 
+ If your images are in .png format, convert them using the included __png_to_jpg.py__ script, by typing `python png_to_jpg.py /path/to/png/images`. 
