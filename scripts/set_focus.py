__author__ = 'Experiment'

import hardware_modules.PiezoController as pc

xController = pc.MDT693A('X')
xController.setVoltage(70)