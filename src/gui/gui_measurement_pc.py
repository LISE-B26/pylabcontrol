# this is the gui for the measurment pc
# this gui only loads dummy scripts and instruments

import sys

from src.core import qt_b26_gui

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)



instruments = {
    # 'inst_dummy': 'DummyInstrument',
    'zihf2':'ZIHF2',
    'pressure gauge': 'PressureGauge'}

scripts= {


    # 'counter': 'ScriptDummy',
    #
    #
    # 'dummy script with inst': {
    #     'script_class': 'ScriptDummyWithInstrument',
    #     'instruments': {'dummy_instrument': 'inst_dummy'}
    # },
    #
    # 'QT counter' : 'ScriptDummyWithQtSignal',

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

# {"zihf2": "ZIHF2", "inst": 'INST'} => param = {"zihf2": &ZIHF2, 'inst': &sacbs;}

# Zi_Sweeper(*param)

probes = {
    # 'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
    # 'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
    'ZI(R)': {'probe_name': 'R', 'instrument_name': 'zihf2'},
    'ZI(X)': {'probe_name': 'X', 'instrument_name': 'zihf2'}
    # 'Chamber Pressure' : { 'probe_name': 'pressure', 'instrument_name': 'pressure gauge'}
          }

ex = qt_b26_gui.ControlMainWindow(instruments, scripts, probes)
ex.show()
ex.raise_()
sys.exit(app.exec_())
