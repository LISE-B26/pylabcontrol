# this is the gui for the measurment pc
# this gui only loads dummy scripts and instruments

import sys

from src.core import qt_b26_gui

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)


# =========== for right PC =================================
instruments = {
    # 'inst_dummy': 'DummyInstrument',
    'zihf2':'ZIHF2',
    'pressure gauge': 'PressureGauge',
    'cryo station': 'CryoStation',
    'spectrum analyzer': 'SpectrumAnalyzer',
    'microwave generator': 'MicrowaveGenerator'
}

scripts= {


    'u-wave spectra': {
        'script_class': 'KeysightGetSpectrum',
        'instruments':{
        'spectrum_analyzer' : 'spectrum analyzer'
        }
    },

    'u-wave spectra vs power': {
        'script_class': 'KeysightSpectrumVsPower',
        'instruments':{'cryo_station' : 'cryo station'},
        'scripts': {'get_spectrum': {
            'script_class': 'KeysightGetSpectrum',
            'instruments':{'spectrum_analyzer' : 'spectrum analyzer'}
            }
        }
    },



    # 'u-wave spectra vs power': {
    #     'script_class': 'MWSpectraVsPower',
    #     'instruments':{
    #     'microwave_generator' : 'microwave generator',
    #     'cryo_station' : 'cryo station',
    #     'spectrum_analyzer' : 'spectrum analyzer'
    #     }
    # },

    'ZI sweep' : {
        'script_class': 'ZISweeper',
        'instruments': {'zihf2': 'zihf2'}
    },

    'High res scan' : {
        'script_class': 'ZISweeperHighResolution',
        'scripts': {
            'zi sweep' : {
                'script_class': 'ZISweeper',
                'instruments': {'zihf2': 'zihf2'}
            }
        }
    }

}



probes = {
    # 'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
    # 'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
    'ZI (R)': {'probe_name': 'R', 'instrument_name': 'zihf2'},
    'ZI (X)': {'probe_name': 'X', 'instrument_name': 'zihf2'},
    'T (platform)': {'probe_name': 'platform_temp', 'instrument_name': 'cryo station'},
    'T (stage 1)': {'probe_name': 'stage_1_temp', 'instrument_name': 'cryo station'},
    'T (stage 2)': {'probe_name': 'stage_2_temp', 'instrument_name': 'cryo station'}
    # 'Chamber Pressure' : { 'probe_name': 'pressure', 'instrument_name': 'pressure gauge'}
          }




# #  =========== for left PC =================================
#
#
#
# #maestro
# # 5 - green
# # 4 - ir
# # 3
# # 2
# # 1 - filter wheel
# # 0 - flip mount
# instruments = {
#     'IR block': 'MaestroBeamBlock',
#     'Green block': 'MaestroBeamBlock',
#     'filter wheel': 'MaestroFilterWheel',
#     'white light': 'MaestroBeamBlock'
# }
#
# scripts = {}
#
# probes = {}
path_to_default = ''

path_to_default = 'C:\\Users\\Experiment\\gui_settings.b26guix'

try:
    ex = qt_b26_gui.ControlMainWindow(path_to_default)
except AssertionError:
    ex = qt_b26_gui.ControlMainWindow(instruments, scripts, probes)
ex.show()
ex.raise_()
sys.exit(app.exec_())
