__author__ = 'Experiment'

import functions.Focusing as f

# a = Focus.scan(70, 90, 50, 'Z', waitTime = .1)
# sets the focus
# a = f.Focus.scan(20, 90, 50, 'Z', waitTime = .1, APD=True)

# a = f.Focus.scan(20, 90, 40, 'Z', waitTime = .1, APD=True)


scan_range_roi = {
    "dx": 0.1,
    "dy": 0.1,
    "xPts": 20,
    "xo": 0.0,
    "yPts": 20,
    "yo": 0.0
}

a = f.Focus.scan(20, 90, 10, 'Z', waitTime = .1, APD=True, scan_range_roi = scan_range_roi)