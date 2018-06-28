Importing an Instrument or Script into the GUI
******************************************************

This guides you through the steps of importing an instrument or script into the GUI

Prerequisites
==================
It is assumed that you have a .py file containing a class inheriting from Instrument or Script. You must be able to
create an instance of this class on the computer you are planning to use the GUI on. Also, .py file must be in a folder
that contains a __init__.py file. For a more thorough understanding of __init__.py files, see
`this StackOverflow thread <https://stackoverflow.com/questions/448271/what-is-init-py-for>`_. Otherwise, it is very
likely you want a blank text file named __init__.py in the same directory as your .py code.

Overview
==========
To be able to import an instrument or script into the GUI, you must first create a .b26 file from the .py file.
Afterwards, you can import the .b26 file into the GUI. This is all done within the pylabcontrol GUI.

Importing Scripts of Instruments
======================================
1. Run the GUI.
2. Go to File->convert instrument or script .py file to .b26 file
3. Make sure you select the correct source folder.
4. Go to the Instrument or Script tab, and select the Import Instrument or Import Script button.
5. Select the .b26 file from the right directory on the computer, and drag the resulting instrument or script from the
right panel to the left panel.
6. Press "ok". The resulting Script or Instrument should be imported into the GUI


Note that when you import a Script, all of the requisite instruments and subscripts will also be uploaded.

