__author__ = 'Experiment'

import functions.Focusing as f

# a = Focus.scan(70, 90, 50, 'Z', waitTime = .1)
# sets the focus
# a = f.Focus.scan(20, 90, 50, 'Z', waitTime = .1, APD=True)

# a = f.Focus.scan(20, 90, 40, 'Z', waitTime = .1, APD=True)

a = f.Focus.scan(45, 51, 100, 'Z', waitTime = .1, APD=True)