Creating a Script
***************************************************************************************************

This guide goes through the steps of creating an instrument with pylabcontrol

Overview
==========
To create a script, one must create a class that inherits from Script (pylabcontrol.core.Script), and implements the following:

1. _DEFAULT_SETTINGS: class variable containing the settings for the script. This must be of Parameter type.

2. _INSTRUMENTS: a dictionary whose key-value pairs are instrument names (strings) and the class names of Instruments

3. _SCRIPTS: a dictionary whose key-value pairs are script names (strings) and the class names of Scripts

4. _function(): function that contains the main logic of the script.

5. _plot(): function that dictates how the script will plot data during its execution.

6. _update_plot() (optional): function that dictates how the script will update an existing plot during its execution.

7. self.data: dictionary containing the data

Examples
===========
There are two main places you can go for examples: First, take a look at
`the barebones script examples in the github repository
<https://github.com/LISE-B26/pylabcontrol/tree/master/pylabcontrol/scripts>`_.
Second, there are several scripts written for the experiments done in the Lukin Lab,
located on `the b26_toolkit github page <https://github.com/LISE-B26/b26_toolkit/tree/master/b26_toolkit/scripts>`_.

_DEFAULT_SETTINGS
==========================

The _DEFAULT_SETTINGS class variable is a Parameter that contains all of the parameters for the current script. It plays
the same role as _DEFAULT_SETTINGS plays for instruments.


_INSTRUMENTS and _SCRIPTS
=========================
THe _INSTRUMENTS and _SCRIPTS class variables contain dictionaries with key-value pairs 'name':ClassName. They contain
the instruments (of type Instrument) and (sub)scripts (or type Script) that will be used when running the script.
Note that the classes must be imported in the Script file.


self.data
==============

Every class inheriting from Script has an instance variable self.data that contains key-value pairs of data. The key is
a string description of the data, and the value is the data. The data can either be a single number, a 1D list of
numbers, or a 2D list of numbers. No other data types are currently supported.

_function()
============
This function is called upon

During the execution of _function(), you should be updating self.data.

The Progress Bar
================
The progress bar in the pylabcontrol gui will only update if it is explicitly updated in your _function. To update
the progress bar in _function(), call

    .. code:: python

        def _function():
            # ...
            self.updateProgress(current_progress)
            # ...

within _function(). current_progress must be an integer between 0 and 100 inclusive.

Time estimates are inferred based on the elapsed time and the current progress.

Logging
=======
Often, it is useful to have scripts output text updates during its execution; Scripts can send messages to the log in
the GUI during execution. To utilize this feature in your code, simply pass a string to the self.log() function, like
so:

    .. code:: python

        def _function():
            # ...
            self.log('Subroutine was successful')
            # ...

and at that point in the execution, 'Subroutine was successful' will be displayed in the GUI's log.

The start and end time of the scripts is always outputted to the log.


_plot()
=======
This function is called each time updateProgress() is called in _function(), and determines how to visualize the current
point in the script. Usually, this means plotting the data located in self.data to one (or both) of the two axes objects.

Note that _plot() will be passed in a length-2 list of axes objects from the GUI. For more information on axes objects,
see `here <https://matplotlib.org/api/axes_api.html>`_.


_update_plot()
==============
If this function is defined, it will be called after the script has called _plot(). This function is optional, and
provides a method for optimizing matplotlib's refresh rate for visualizations. For more information, see the
FAQ.


Testing
========
If you wish to test your script before running it in the GUI, you are welcome to create an instance of the script and
then run

    .. code:: python

        if __name__ == '__main__':
            script_instance = MyScript()
            script_instance.run()

The run() function will call _function(). Although this is an option, it is recommended you directly rest your
script with the GUI, since plotting is most easily tested this way.


