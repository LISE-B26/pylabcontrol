
sweep =  {
    'start' : {'value': 0.0, 'valid_values': None, 'info':'start value of sweep', 'visible' : True},
    'stop' : {'value': 0.0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
    'samplecount' : {'value': 0, 'valid_values': None, 'info':'number of data points', 'visible' : True},
    'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True},
    'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True},
    'bandwidthcontrol' : {'value': 2, 'valid_values': [2], 'info':'2 = automatic bandwidth control', 'visible' : True},
    'scan' : {'value': 0, 'valid_values': [0, 1, 2], 'info':'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)', 'visible' : True},
    'loopcount' : {'value': 1, 'valid_values': None, 'info':'number of times it sweeps', 'visible' : False},
    'averaging/sample' : {'value': 0, 'valid_values': None, 'info':'number of samples to average over', 'visible' : True}
}

find_max = {
    'param1':1,
    'param2':2,
}

SETTINGS_DICT = {
        'sweep' : sweep,
        'find_max' : find_max,
        'sweep and find max' :{
            'sweep' : sweep,
            'find_max' : find_max
        }
}

