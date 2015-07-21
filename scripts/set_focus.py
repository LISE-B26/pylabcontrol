__author__ = 'Experiment'

import hardware_modules.PiezoController as pc

def set_focus(channel, voltage):
    xController = pc.MDT693A(channel)
    xController.setVoltage(voltage)