# dictionaries that contain the settings
# each value has some metadata:
# - value:          the actual value
#  - valid_values:  allows values of type
#  - info:          info that is shown as tooltip
#  - visible:       if displayed in tree
#  - target:        optional: required for hardware settings, this is the hardware module that receives the parameter





# ============= SWEEP SETTING ====================================
# ==================================================================
SWEEP_SETTINGS =  {
    'start' : {'value': 0.0, 'valid_values': (float, int), 'info':'start value of sweep', 'visible' : True, 'target' : 'ZI sweep'},
    'stop' : {'value': 0.0, 'valid_values': (float, int), 'info':'end value of sweep', 'visible' : True, 'target' : 'ZI sweep'},
    'samplecount' : {'value': 0, 'valid_values': int, 'info':'number of data points', 'visible' : True, 'target' : 'ZI sweep'},
    'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True, 'target' : 'ZI sweep'},
    'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True, 'target' : 'ZI sweep'},
    'bandwidthcontrol' : {'value': 2, 'valid_values': [2], 'info':'2 = automatic bandwidth control', 'visible' : True, 'target' : 'ZI sweep'},
    'scan' : {'value': 0, 'valid_values': [0, 1, 2], 'info':'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)', 'visible' : True, 'target' : 'ZI sweep'},
    'loopcount' : {'value': 1, 'valid_values': int, 'info':'number of times it sweeps', 'visible' : False, 'target' : 'ZI sweep'},
    'averaging/sample' : {'value': 0, 'valid_values': int, 'info':'number of samples to average over', 'visible' : True, 'target' : 'ZI sweep'}
}

# ============= Dummy SETTING ====================================
# ==================================================================
find_max = {
    'df' : {'value': 1.0, 'valid_values': (float, int), 'info':'frequency step of fine sweep', 'visible' : True},
    'N': {'value': 21, 'valid_values': int, 'info':'number of datapoints step of fine sweep', 'visible' : True}
}


# ============= GENERAL SETTING ====================================
# ==================================================================

MAIN_SETTINGS = {
    "record_length" : {'value': 100, 'valid_values': int, 'info': 'length of data shown in liveplot', 'visible' : True},
    "parameters_PI" : {
        "sample_period_PI" : {'value': int(8e5), 'valid_values': int, 'info': 'time step of PI loop in clock cycles (40MHz)', 'visible' : True},
        "gains" : {
            'proportional': {'value': 0, 'valid_values': float, 'info': 'proportional gain of PI loop', 'visible' : True},
            'integral': {'value': 0, 'valid_values': float, 'info': 'integral gain of PI loop', 'visible' : True}
        },
        "setpoint" : {'value': 0, 'valid_values': int, 'info': 'setpoint of PI loop (in bits)', 'visible' : True},
        "piezo" : {'value': 0, 'valid_values': int, 'info': 'output to piezo (in bits)', 'visible' : True}
    },
    "parameters_Acq" : {
        "sample_period_acq" : {'value': 100, 'valid_values': int, 'info': 'time step of acquisition loop in clock cycles (40MHz)', 'visible' : True},
        "data_length" :  {'value': int(1e5), 'valid_values': int, 'info': 'number of datapoints for fast acquisition', 'visible' : True},
        "block_size" : {'value': 2000, 'valid_values': int, 'info': 'number of data points that are read out at once', 'visible' : True},
    },
    "detector_threshold" : {'value': 50, 'valid_values': int, 'info': 'detector value for which detectors are considered balanced', 'visible' : True},
    "data_path" : {'value': "Z:/Lab/Cantilever/Measurements/20160209_InterferometerStabilization/data", 'valid_values': str, 'info': 'main path where data is stored', 'visible' : True},
    "hardware" : {
        "serial_port_maestro" : {'value': "COM5", 'valid_values': ["COM5"], 'info': 'com port of maestro controler', 'visible' : True},
        "parameters_whitelight" : {
            "channel" : {'value': 0, 'valid_values': [0,1,2,3,4,5], 'info': 'channel where white light is connected', 'visible' : True},
            "position_list" : {
                'on': {'value': 4*600, 'valid_values': int, 'info': 'on position of white light', 'visible' : True},
                'off':{'value': 4*1750, 'valid_values': int, 'info': 'off position of white light', 'visible' : True}
            },
            "settle_time" : {'value': 0.2, 'valid_values': float, 'info': 'wait time after position has been switched', 'visible' : True}
        },
        "parameters_filterwheel" : {
            "channel" : {'value': 1, 'valid_values': [0,1,2,3,4,5], 'info': 'channel where filter wheel is connected', 'visible' : True},
            "position_list" : {
                'ND1.0': {'value': 4*600, 'valid_values': int, 'info': 'on position of ND1 filter', 'visible' : True},
                'LP':{'value': 4*1550, 'valid_values': int, 'info': 'off position of LP filter', 'visible' : True},
                'ND2.0':{'value': 4*2500, 'valid_values': int, 'info': 'off position of ND2 filter', 'visible' : True}
            },
            "settle_time" : {'value': 0.2, 'valid_values': float, 'info': 'wait time after position has been switched', 'visible' : True}
        },
        "parameters_camera" : {
            "channel" : {'value': 2, 'valid_values': [0,1,2,3,4,5], 'info': 'channel where white light is connected', 'visible' : True},
            "position_list" : {
                'on': {'value': 4*600, 'valid_values': int, 'info': 'on position of camera', 'visible' : True},
                'off':{'value': 4*1750, 'valid_values': int, 'info': 'off position of camera', 'visible' : True}
            },
            "settle_time" : {'value': 0.2, 'valid_values': float, 'info': 'wait time after position has been switched', 'visible' : True}
        },
        "channel_beam_block_IR" : {'value': 4, 'valid_values': [0,1,2,3,4,5], 'info': 'channel where beam block (IR) is connected', 'visible' : True},
        "channel_beam_block_Green" : {'value': 5, 'valid_values': [0,1,2,3,4,5], 'info': 'channel where beam block (green) is connected', 'visible' : True},
    "kinesis_serial_number" :  {'value': 83832028, 'valid_values': [83832028], 'info': 'serial number of thorlabs motor', 'visible' : True},
    },
    'live_data_ids' : {
        'AI1': True, 'AI1_raw': True,  'min': False, 'max': True, 'mean': True, 'stddev': True
    }
}

# ============= SCRIPT SETTING ====================================
# ==================================================================
# this can take in some other settings
SCRIPTS = {
        'sweep' : SWEEP_SETTINGS,
        'sweep and find max' :{
            'sweep' : SWEEP_SETTINGS,
            'find_max' : find_max
        }
}

