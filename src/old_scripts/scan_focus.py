__author__ = 'Experiment'

from src import old_functions as f

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

if __name__ == '__main__':
    a = f.Focus.scan(32.5, 42.5, 40, 'Z', waitTime = .1, APD=True, scan_range_roi = scan_range_roi)