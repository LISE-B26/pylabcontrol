__author__ = 'Experiment'

import functions.Focusing as f

# a = Focus.scan(70, 90, 50, 'Z', waitTime = .1)
# sets the focus
a = f.Focus.scan(49, 55, 150, 'Z', waitTime = .1, APD=True)