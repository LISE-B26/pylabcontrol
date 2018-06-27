.. _faq:
Frequenty Asked Questions
*********************************

Q1. **I have found an issue or annoyance in the software. How can I let the developers know of the issue?**

    A: Feel free to leave any feedback on `the issues tracker <https://github.com/LISE-B26/pylabcontrol/issues>`_.

Q2. **Why are there separate plot() and update_plot() functions for Scripts?**

    A: matplotlib, the plotting library used in pylabcontrol, was not designed for plotting data quickly.
    In many situations, the GUI might plot script updates more quickly than matplotlib can keep up.
    To get around this issue, many developers have come up with tricks to make matplotlib plot faster; these tricks
    normally involve manually updating only the minimal things. For more information, see many of the `scripts in
    b26_toolkit <https://github.com/LISE-B26/b26_toolkit/tree/master/b26_toolkit/scripts>`_
    as well as many blog posts online, `like this one <http://bastibe.de/2013-05-30-speeding-up-matplotlib.html>`_.

Q3. **Why is update() being called several times during an instrument's execution?**

    A: In the current version of the software, one can update instruments by writing

    .. code:: python

        instrument_instance.parameter1 = value

    despite the fact that all of the instrument settings are located in the instance variable self.settings().
    To achieve this, we tweaked our Instrument class to always check to see if an instance variable is supposed to
    be an instrument parameter by passing it into update and checking if an error occurs. Thus, update() is actually
    called every time an instance variable is set.

