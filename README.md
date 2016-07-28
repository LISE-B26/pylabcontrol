PyLabControl is a software environment for controlling scientific equipment for laboratory experiments. It
+	interacts with any equipment that supports a python interface,
+	executes user-created scripts for complex experimental control sequences,
+	visualizes experimental data utilizing the standard python matplotlib library
+	streamlines data acquisition, storage, and retrieval

PyLabControl is built on python 2.7.11, with extensive use of pyQT for the general user interface. It was built by Arthur Safira, Jan Gieseler, and Aaron Kabcenell in the Lukin Group at Harvard University. It is distributed under the BLAH license.


## Getting Started
The software was developed and tested with python 2.7.11 on 64-bit Windows 7. Prior to installation, we recommend installing the latest anaconda python package for python version 2.7, found here: https://www.continuum.io/downloads.

### Installation
The simplest way to install pyLabControl is with the command-line utility pip. To install simply issue the command

`pip install PyLabControl`

Running the GUI
To run the gui, open a python interpreter and write

```
import pyLabControl
PyLabControl.run()
```

Before the gui runs, you will be prompted to select a path to save gui configuration files.

### Getting to know the GUI: Basics
The loaded gui should look like the one below:

(PICTURE)



### Importing Instruments
Although you have not coded any instruments

### Importing Scripts


If you are interested in importing your own instruments or scripts, pelase do not hesitate to reach out to the authors of pyLabControl.

### B26_Toolkit
This software was created to streamline experiments done in the Lukin Lab; the instruments and scripts utilized there can be imported into pyLabControl by installing the b26_toolkit. More information can be found here: ()

### FAQ
