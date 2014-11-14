Data Collection using the Ultrasound with the Kinect
===

 >This manual will show how to set up and collect data from a subject. The end result will be a folder for the individual subject that holds the ultrasound video, Kinect data and coordinates, stimulus list, as well as individual frames of the tongue images.
 
Setting Up the Hardware Before the Subject Arrives: NEED PICTURE
---
 + Make sure the _ultrasound_ is connected to the _lockbox_

 + The _svideo_ cable connects to the back of the ultrasound

 > It is the cable that connects the _ultrasound_ and the _lockbox_

 > The _lockbox_ has a label for this _svideo_ cable

 >Important: if it is not connected, make sure the _ultrasound_ is off before connecting, otherwise it may malfunction

 + _Microphone amplifier_ should be connected to _computer_

 >It connects in the spot with the pink ring around it

 + Make sure the _lockbox_ is on

 > There should be a blue light on the _lockbox_ that shows that it is on

 + If it does need to be turned on, press the _power button_ on the _lockbox_

 >When you do this a box will pop up on the monitor which you should __exit__ out of

Setting up the Ultrasound Software with the Kinect
---
 + Turn on the _ultrasound_

 + There is a _power button_ in the top left corner of the _ultrasound_

INCLUDE PICTURE

 + Test the video feed of the _ultrasound_

 + There should be a black screen on the _Titan_ with white grain that shows the _ultrasound_ is on and functioning

 + Make sure the _Kinect_ is connected to the _computer_

 > The _USB cord_ connects to the front of the _computer_

 + On the main monitor, locate the __ultrasound icon__ and _double click_ on it

 > Two new windows should open, a __Kinect__ window and an __ultrasound__ window

 + Move the __Kinect__ window to the right of the __ultrasound__ window

 + On the monitor, locate the __stimulus display__ icon

 + Click __stimuli.py__ and a new window should open

 + Close the __explorer__ window

 > The stimuli will be a group of words in any language that the subjects will be prompted with in a random order

 + To determine how many times these words are repeated, you will be prompted with a screen asking to specify the number of repetitions

 > These repetitions will repeat the same set of words in a different order each time

 + Click _enter_

CREATING A STIM LIST-NEED DIRECTIONS
---

 + A new window will open that says __click to begin__

 + _Drag_ the __click to begin__ window onto the second monitor and resize to fit screen

 + Minimize this window so you can still see the other windows

 + In the __ultrasound__ window, press __preview__ to ensure the image feed from the _ultrasound_ is correct

Setting up Subject
---
 + Sit subject comfortably in chair

 + Mount _microphone_ over subject’s ear

 + Apply a small strip of ultrasound gel to the top of the _probe_ and place directly under subject’s chin to get an image of the tongue and palate

 + Adjust fit of _probe_ to subject

 + Adjust the depth on the _ultrasound_ to make sure the tongue is displaying correctly

NEED TIPS FOR THIS

 > Note: if the video appears extremely zoomed in the best solution is to turn the _ultrasound_ _on_ and _off_ again

Naming the folder
---
 + In the __ultrasound__ window, there is a space entitled __recording ID__

 + In the blank provided, include the study subject number, year, month, day, hour, and minute of the experiment in that order

 > Use leading zeros in the case of single digit months

 >Note: try not to use window’s special characters

 >This creates a separate file that includes the subject number and demographic data that will contain all of the data collected

 + Check the _Kinect_ display

 + Make sure there are no obstructions in the way of the _Kinect_

 + Make sure the _image feed_ recognizes the head of the subject

 > There should be a grid around the face of the subject as shown below
 
Collecting Data
---
 + Press __start__ on the __ultrasound__ window to begin recording

 + The __record button__ should turn red

 > Note: once the recording is done it will turn grey

 + Click on __click to begin__ in the __stimuli__ window

 + Instruct the subject to _click_ through the stimuli as the subject reads the words out loud

 + Once the subject has read through all of the stimuli, the __stimulus display__ window should close

 + Hit __stop__ on the __ultrasound__ window to end the recording

 > Note: do not close this window it is very important that it stays open for post processing

 + The __Kinect__ window should close when you hit __stop__

Post Processing and Saving Data
---
 + Post processing must be done to ensure that all of the proper data is recorded and gathered in the subject’s folder

 + After closing the __Kinect__, an icon entitled __coords__ should appear on the __desktop__

 + Drag the __coords__ icon into the folder you created previously

 + In the top right of the __ultrasound__ window click on the __post processing__ tab

 + Click __Run Post Processing__

 > Note: this may take a while, so be patient

 + A window will pop up that shows it is complete

 + Close out of this window by clicking __ok__

 + Open __Stimulus Display__ icon again

 + Drag the newly created __stimulus_response.csv___ file into the subject’s folder that was created when you filled in the Subject ID

 > This file contains the stimuli, subject information, repition number, and timestamp of when the subject clicked to start each stimuli

 + Open __Kinect Matching__ icon on desktop by _double-clicking_

 + Select the appropriate files for the post processing

 + The __Kinect Matching__ program opens with a window that allows you to select the folders that contain the frames, video, and Kinect video and then combines them into one document labeled __output__

 > Note: Double check with each file you open that they are coming from the correct folder

Can it default to the correct folder?

 + __Frames__: locate in the subject’s folder

 + __Video__: locate the __vidTimes__ section of the subject’s folder

 + __Kinect__: locate the __coords__ section of the subject’s folder

 + __Output__: in the __output file__ box, the __output file__ will be automatically named output and placed in the same folder.

 > If you want it to have another name, you can fill that name into this box

 + Once you have located the four different parts of the folder, hit __process file__

 + A window should pop up that says __file ready__

 + _Close_ the __Kinect Matching__ window

 + _Open_ the folder you created for the subject

 + A new file, entitled __output__ should now be in the folder as well as the __vidTimes, coords__, and __frames__ folders

 + Play the __vidTimes__ video in order to make sure that it recorded properly

 > Do this by _clicking_ the on the __vidTimes__ file within the subject’s folder

 + _Open_ the __output__ file to make sure that the post-processing worked correctly

 > This should have timestamps, frame numbers, and coordinates of the locations of the subject’s head throughout the experiment as shown below