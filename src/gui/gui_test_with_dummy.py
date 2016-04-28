# this gui only loads dummy scripts and instruments

import sys
from src.core import qt_b26_gui

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)



instruments = {'inst_dummy': 'DummyInstrument'}

scripts= {


    'counter': 'ScriptDummy',


    'dummy script with inst': {
        'script_class': 'ScriptDummyWithInstrument',
        'instruments': {'dummy_instrument': 'inst_dummy'}
    },

    'QT counter' : 'ScriptDummyWithQtSignal',

    'dummy script with sub script': {
        'script_class': 'ScriptDummyWithSubScript',
        'scripts': {'sub_script': 'ScriptDummy'}
                        # {
                        #     'script_class': 'ScriptDummy',
                        #     'instruments': {'dummy_instrument': 'inst_dummy'}
                        # }
    }

}



# {"zihf2": "ZIHF2", "inst": 'INST'} => param = {"zihf2": &ZIHF2, 'inst': &sacbs;}

# Zi_Sweeper(*param)

probes = {
    'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
    'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
          }

instruments = {}
scripts= {

    #
    # 'dummy script with inst': 'ScriptDummyWithInstrument',
    # 'script': 'ScriptDummy'

}
probes = {}

settings_file = "Z:\Lab\Cantilever\Measurements\\__tmp\\XX.b26"
# settings_file = ""

print(instruments, scripts, probes)

try:
    ex = qt_b26_gui.ControlMainWindow(settings_file)
except AssertionError:
    ex = qt_b26_gui.ControlMainWindow(instruments, scripts, probes)

# ex = qt_b26_gui.ControlMainWindow(instruments, scripts, probes)
ex.show()
ex.raise_()
sys.exit(app.exec_())
