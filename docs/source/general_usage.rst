Using the pylabcontrol ecosystem for your experiments
*********

Typical Workflow Overview
================
In a typical workflow, a user simply runs the gui, imports a script, sets the parameters of their choosing (in the Script tab),
and presses "Run Script". The script data is saved either to the path indicated in as a script parameter in the GUI,
or if one isn't set, it is saved to the location indicated in the "GUI Settings" tab. Later, a user can import the data
in a separate analysis by using the Script.load_data() function.

What is Saved after Script execution.
============
When a script is saved, the following are saved:

- The data stored in the script --- i.e., the contents of self.data for the Script.

- The script settings. A .b26 file is saved that contains the information about the script, as well as the settings of
the script when it was run.

- A picture of the final plots after the script finished executing.

It is saved either in the location listed in the path variable of the script, or if that is empty, the path listed in
the "GUI Settings" tab.


Using the Datasets Tab
================
Often a script is run but you might be interested in referring back to it at a later --- either choosing to save its current data later,
or wanting to look at its data visualization at a later time. To do so, simply highlight the script in the Scripts tab
and press "Send to Datasets". The script with its current data will be listed in the Datasets tab, and upon clicking on it,
the data will be displayed in the GUI plotting area. The data can also be saved from this tab, using the "save selected" button.