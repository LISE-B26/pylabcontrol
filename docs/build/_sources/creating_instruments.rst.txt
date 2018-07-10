Creating an Instrument
*********************************

This guide goes through the steps of creating an instrument with pylabcontrol

Overview
========
To create an instrument, you need to create a class for that instrument that inherits from pylabcontrol.core.Instrument.
Furthermore, you need to implement the following functions and class variables:

- _DEFAULT_SETTINGS (class variable): this variable contains the default settings for the instrument.

- update() (function): this function updates the instrument parameters.

- _PROBES (class variable): this variable should be left empty.

- read_probes() (function): this function should just 'pass', i.e.,

    .. code:: python

        def read_probes():
            pass

The latter two necessary variable and function are for future updates.

More details about each will be discussed below.

Examples
========
There are two main places you can go for examples: First, take a look at
`the ExampleInstrument class <https://github.com/LISE-B26/pylabcontrol/blob/master/pylabcontrol/instruments/instrument_dummy.py>`_.
The ExampleInstrument class contains a dummy instrument that can be imported into the GUI.

Second, a lot of instruments were created for use in the Lukin Lab, the code for which is located
`here <https://github.com/LISE-B26/b26_toolkit/tree/master/b26_toolkit/instruments>`_. Examples there include
instruments that communicate with GPIB, serial, NI daq_mx, and custom dll's.


Parameters
==========
In pylabcontrol, instrument settings are saved as a custom Parameter datatype (pylabcontrol.core.Parameter); see the full
documentation here. Note that Parameters can be nested, e.g.,
::
    Parameter('voltage_outputs',
                                Parameter('channel_1', 0.0, float, 'channel 1 voltage [V]'),
                                Parameter('channel_2', 0.0, float, 'channel 2 voltage [V]')
              )


_DEFAULT_SETTINGS
==========================
_DEFAULT_SETTINGS is a class variable that is of type Parameter. It contains the default parameters for an instrument.

update()
=================
THe update() function takes a dictionary input and updates each parameter with name given by the key to the value given
by the value.

Testing
=======
When testing the instruments, it is recommended instruments are first tested separately from the GUI (e.g., by creating
and manipulating an instance of the instrument class you created in your python file's __main__.), and then later
the instrument can be imported into the GUI.


