# pylabcontrol
pylabcontrol is a software environment to control scientific equipment for laboratory experiments. 

It
+   provides a GUI for convenient experimental control
+	interacts with any equipment that supports a python interface
+	executes user-created scripts for complex experimental control sequences
+	visualizes experimental data utilizing the standard python [matplotlib](https://matplotlib.org/) library
+	streamlines data acquisition, storage, and retrieval 

pylabcontrol is built on python 3.6, with extensive use of [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) for the general user interface.
It was built by Arthur Safira, Jan Gieseler, and Aaron Kabcenell in the Lukin Group at Harvard University. 
It is distributed under the [GPLv3 license](https://en.wikipedia.org/wiki/GNU_General_Public_License). For more information, see the LICENSE.txt file.

## Getting Started
The software was developed and tested with python 3.6 on 64-bit Windows 7. Prior to installation, install the latest 
Anaconda distribution for python version 3.6, as it contains some extra dependencies this project utilizes.
You can find the latest Anaconda distribution [here](https://www.continuum.io/downloads). 

### Installation
There are two main ways to install pylabcontrol: via pip, the python package manager, or directly from the source via
github. The former is easier, while the latter gives more explicit access to the source code.

#### Via pip (Beginner)
The simplest way to install pylabcontrol is with the command-line utility pip. To install simply issue the command

```>>> pip install pylabcontrol```

in the windows command-line interface. To run the gui, open commandline and run

``` >>> pylabcontrol```

Before the gui runs, you will be prompted to select a path to save gui configuration files.

#### Via git (Intermediate/Advanced)
If you are interested in hosting the source code more directly, you can clone from our git page:

```>>> git clone https://github.com/LISE-B26/pylabcontrol.git```

You should have the resulting directory on your local filesystem. If you are using PyCharm for development, 
it is recommended that you 
+ confirm you are using the right python environment (Anaconda's latest python 3.x),
+ have set pylabcontrol/pylabcontrol to be the sources root, and 
+ have configured pycharm to include the sources root in the pythonpath before execution of the code.

To launch the gui, simply run the file pylabcontrol\pylabcontrol\gui\launch_gui.py . Before the gui runs, you will be prompted to select a path to save gui configuration files.

### Getting to know the GUI: Basics
The loaded gui should look like the one below (except that there will be no scripts and the plots will be blank):

![pylabcontrol GUI](/docs/images/main_window.png?raw=true "pylabcontrol GUI")

#### Brief GUI walkthrough
The GUI is made up of three main areas, labelled in the above screenshot.
+ **The top left** portion of the GUI has four tabs that contain the loaded scripts and instruments, probes to monitor values from some of the loaded instruments, and a dataset manager.
These will be discussed in more detail below, after scripts and instruments are imported into the GUI.
+ **The bottom left** portion of the GUI comprises the log and GUI configuration details. The log gives text updates during the execution of scripts and when instruments
are toggled. The GUI configuration tab has filepaths for saving data, as well as GUI configuration information.
+ **The entire right half** of the GUI is for data visualization, and is composed of a major and minor plotting area. 
These are used to visualize data, both during scripts and after their execution.

To see these in action, we need to import an instrument and/or script.

#### Creating script and instrument files
At this point, the GUI should have properly launched, and it's time to start interacting with instruments.

TBA

#### Importing Scripts
No scripts will be in the GUI the first time it is launched; scripts will have to separately be loaded in.  A few 
dummy scripts are provided to better understand the interaction model with the GUI.

Navigate to the 'Scripts' tab in the top left of the GUI, and press "Import Scripts". The following dialog should show:
![Load dialog](/docs/images/load_dialog.png?raw=true "Load dialog")
Find the .b26 file you created, and be sure to the click and drag the Dummy Script to the left pane. Press Ok, and the script should be shown in the GUI. 

The script loading dialog also allows you to create "iterator" scripts, i.e., basic loops over preexisting scripts. You can find more about iterator scripts [here.](docs/iterator_scripts.md)

#### Importing Instruments
No instruments will be in the GUI the first time it is launched; instruments will have to separately be loaded in. 

Navigate to the 'Instruments' tab in the top left of the GUI, and press "Import Instruments". Find the .b26 file you created, 
and be sure to the click and drag the Dummy Instrument to the left pane. Press Ok, and the instrument should be shown in the GUI. 

#### .b26 files
Settings and configurations are saved in json files with .b26 extension.
Since these files can become quite large for complex scripts, we recommend a json viewer to look at them (e.g. https://jsonviewer.codeplex.com/).

#### b26_toolkit
This software was created to streamline experiments done in the Lukin Lab; 
the instruments and scripts utilized there can be imported into pylabcontrol by installing b26_toolkit. 
More information can be found here: https://github.com/LISE-B26/b26_toolkit .

## FAQ
+ **Does this work with other operating systems?**

While only extensively tested on 64-bit Windows 7, we expect the GUI to work on other versions of windows, LINUX, and Mac OSX.
However, we do not officially support other platforms.

+ **How can we send feedback?**

Feel free to create an issue on the issue tracker if you find any bugs, or contact the authors directly.

## Funding
pylabcontrol has been partially funded by the European Union (H2020-MSCA-IF-2014 under REA grant Agreement No. 655369)

![Marie Skłodowska-Curie Action](/docs/images/MC_EU_logo_small.png?raw=true "Marie Skłodowska-Curie Action")

