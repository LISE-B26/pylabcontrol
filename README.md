# PyLabControl
PyLabControl is a software environment to control scientific equipment for laboratory experiments. 

It
+	interacts with any equipment that supports a python interface
+	executes user-created scripts for complex experimental control sequences
+	visualizes experimental data utilizing the standard python matplotlib library
+	streamlines data acquisition, storage, and retrieval 

PyLabControl is built on python 2.7.x, with extensive use of pyQT for the general user interface. 
It was built by Arthur Safira, Jan Gieseler, and Aaron Kabcenell in the Lukin Group at Harvard University. 
It is distributed under the GPLv3 license. For more information, see LICENSE.txt .



## Getting Started
The software was developed and tested with python 2.7.x on 64-bit Windows 7. Prior to installation, install the latest 
Anaconda distribution for python version 2.7.x, as it contains some extra dependencies this project utilizes.
You can find the latest Anaconda distribution here: found here: https://www.continuum.io/downloads . 

### Installation
The simplest way to install pyLabControl is with the command-line utility pip. To install simply issue the command

```>>> pip install PyLabControl```

in the windows command-line interface.

#### Creating script and instrument files
instrument and script configurations are saved in files with a .b26 extension
To export the default configurations of the scripts and instruments that come with PyLabControl, open commandline and run

``` >>> PyLabControl --export path_to_target_folder```

where path_to_target_folder is the path to the folder where you want to save the .b26 files (e.g. `PyLabControl --export c:\User\b26_files`).

#### Running the GUI
To run the gui, open commandline and run

``` >>> PyLabControl --gui```

Before the gui runs, you will be prompted to select a path to save gui configuration files.
ProTip: After you have loaded the gui for the first time you can later also pass the path to the config file (e.g. `PyLabControl --gui c:\User\PyLabControl\config.b26`)

### Getting to know the GUI: Basics
The loaded gui should look like the one below (except that there will be no scripts and the plots will be blank):

![PyLabControl GUI](/docs/images/main_window.png?raw=true "PyLabControl GUI")

#### Brief GUI walkthrough
The GUI is made up of four main areas, labelled in the above screenshot.
+ **The top left** portion of the GUI has four tabs that contain the loaded scripts and instruments, probes to monitor values from some of the loaded instruments, and a dataset manager.
These will be discussed in more detail below, after scripts and instruments are imported into the GUI.
+ **The bottom left** portion of the GUI comprises the log and GUI configuration details. The log gives text updates when instruments
are toggled and during the execution of scripts. The GUI configuration tab has filepaths for saving data, as well as GUI configuration information.
+ **The entire right half** of the GUI is for data visualization, and is composed of a major and minor plotting area. 
These are used to visualize data, both during scripts and after their execution.

To see these in action, we need to import an instrument and/or script.

#### Importing Scripts
No scripts will be in the GUI the first time it is launched; scripts will have to separately be loaded in.  A few 
dummy scripts are provided to better understand the interaction model with the GUI.

Navigate to the 'Scripts' tab in the top left of the GUI, and press "Import Scripts". The following dialog should show:
![Load dialog](/docs/images/load_dialog.png?raw=true "Load dialog")
Find the .b26 file you created, and be sure to the click and drag the Dummy Script to the left pane. Press Ok, and the script should be shown in the GUI. 

The script loading dialog allows also to create iterator scripts. There are four types of iterator scripts:
    - loop
    - parameter sweep
    - iter points (only supported with b26_toolkit)
    - iter Nvs (only supported with b26_toolkit)

you can find more about [iterator scripts here!](docs/iterator_scripts.md)

If you are interested in importing your own instruments or scripts soon, please do not hesitate to reach out to the authors of PyLabControl.

#### Importing Instruments
No instruments will be in the GUI the first time it is launched; instruments will have to separately be loaded in. 

Navigate to the 'Instruments' tab in the top left of the GUI, and press "Import Instruments". Find the .b26 file you created, 
and be sure to the click and drag the Dummy Instrument to the left pane. Press Ok, and the instrument should be shown in the GUI. 

#### .b26 files
Settings and configurations are saved in json files with .b26 extension.
Since these files can become quite large for complex scripts, we recommend a json viewer to look at them (e.g. https://jsonviewer.codeplex.com/).

#### B26_Toolkit
This software was created to streamline experiments done in the Lukin Lab; 
the instruments and scripts utilized there can be imported into PyLabControl by installing b26_toolkit. 
More information can be found here: https://github.com/LISE-B26/b26_toolkit

## FAQ
+ **Does this work with other operating systems?**

While only extensively tested on 64-bit Windows 7, the GUI should work on other versions of windows, LINUX, and Mac OSX.
However, we do not officially support other platforms at this time.

+ **How can we send feedback?**

Feel free to create an issue on the issue tracker if you find any bugs, or contact the authors directly.
