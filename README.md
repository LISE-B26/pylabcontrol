PyLabControl is a software environment to control scientific equipment for laboratory experiments. It
+	interacts with any equipment that supports a python interface
+	executes user-created scripts for complex experimental control sequences
+	visualizes experimental data utilizing the standard python matplotlib library
+	streamlines data acquisition, storage, and retrieval 

PyLabControl is built on python 2.7.x, with extensive use of pyQT for the general user interface. 
It was built by Arthur Safira, Jan Gieseler, and Aaron Kabcenell in the Lukin Group at Harvard University. 
It is distributed under the BLAH license.


## Getting Started
The software was developed and tested with python 2.7.x on 64-bit Windows 7. Prior to installation, install the latest 
Anaconda python package for python version 2.7, as it contains some extra dependencies this project utilizes.
You can find the latest Anaconda distribution here: found here: https://www.continuum.io/downloads . 

### Installation
The simplest way to install pyLabControl is with the command-line utility pip. To install simply issue the command

```>>> pip install PyLabControl```

Running the GUI
To run the gui, open commandline and run

``` >>> PyLabControl ```

Before the gui runs, you will be prompted to select a path to save gui configuration files.

### Getting to know the GUI: Basics
The loaded gui should look like the one below:

(PICTURE)

#### Brief GUI walkthrough
The GUI is made up of four main areas, labelled in the above screenshot.
+ The top left part of the GUI has four tabs that contain the loaded scripts and instruments, 
a monitor to monitor values from some of the loaded instruments, 
and a dataset manager. These will be discussed in more detail below, after scripts and instruments are imported into the GUI.
+ The bottom left portion of the GUI comprises the log and GUI configuration details. The log gives text updates when instruments
are toggled and during the execution of scripts. The GUI configuration tab has filepaths for saving data, as well as GUI configuration information.
+ The entire right half of the GUI is for data visualization, and is composed of a major and minor plotting area. 
These are used to visualize data, both during scripts and after their execution.

To see these in action, we need to import an instrument and/or script.

### Importing Instruments
No instruments will be in the GUI the first time it is launched; instruments will have to separately be loaded in. A
dummy instrument is provided to better understand the interaction model with the GUI.

Navigate to the 'Instruments' tab in the top left of the GUI, and press "Import Instruments". Find the .b26 file you created, 
and be sure to the click and drag the Dummy Instrument to the left pane. Press Ok, and the instrument should not be shown in the GUI. 

### Importing Scripts
No scripts will be in the GUI the first time it is launched; scripts will have to separately be loaded in. The steps are exactly as above, ...

Custom instruments and scripts will be supported in a later release. 
If you are interested in importing your own instruments or scripts soon, pelase do not hesitate to reach out to the authors of pyLabControl.

### B26_Toolkit
This software was created to streamline experiments done in the Lukin Lab; the instruments and scripts utilized there can be imported into pyLabControl by installing b26_toolkit. More information can be found here: ()

### FAQ
