Tutorial: Creating a Script
*********

This guide goes through the steps of creating an instrument with pylabcontrol

Overview
========
To create a script, one must create a class that inherits from Script (pylabcontrol.core.Script), and implements the following:
1. _DEFAULT_SETTINGS: class variable containing the settings for the script. This must be of Parameter type.
2. _INSTRUMENTS: a dictionary whose key-value pairs are instrument names (strings) and the class names of Instruments
3. _SCRIPTS: a dictionary whose key-value pairs are script names (strings) and the class names of Scripts
4. _function: this is where the main script logic goes.
5. _plot(): This is where you write the code that dictates how the script will plot data during its execution.
6. _update_plot() (optional): This is where you write the code that dictates how the script will update an existing plot
 during its execution.

Examples
========
There are two main places you can go for examples: First, take a look at
`the barebones script examples in the github repository
<https://github.com/LISE-B26/pylabcontrol/tree/master/pylabcontrol/scripts>`.
Second, there are several scripts written for the experiments done in the Lukin Lab,
located on `the b26_toolkit github page <https://github.com/LISE-B26/b26_toolkit/tree/master/b26_toolkit/scripts>.

_DEFAULT_SETTINGS
==========================


_INSTRUMENTS and _SCRIPTS
=================

_function()
=========

_plot()
=====


The Progress Bar
================
The progress bar in the pylabcontrol gui will only update if it is explicitly updated in your _function.

Time estimates are inferred based on the elapsed time and the current progress.

Logging
=======
Often, it is useful to have scripts output text updates during its execution; Scripts can send messages to the log in
the GUI during execution. To utilize this feature in your code, simply pass a string to the self.log() function, like
so:
::
    self.log('Subroutine was successful')

The start and end time of the scripts is always outputted to the log.

_update_plot()
==============



