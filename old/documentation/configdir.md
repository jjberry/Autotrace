Configdir.py
===
>This script arranges training data into the directory
    structure that TrainNetwork.py expects.

Usage
---
+ Open [configdir.py](../configdir.py)
+ run the script: python configdir.py
+  This file should be placed in the directory with the __.jpg/.png__
    and corresponding __.traced.txt__ files, as well as __ROI_config.txt.__
+ Running this script produces the directories __Subject1/__, __traces/__ and __Subject1/IMAGES/__, as well as __TongueContours.csv__. 
+ __ROI_config.txt__
    is moved into __Subject1/__.
