__author__ = 'Experiment'

from src.old_hardware_modules import PiezoController as pc


def set_focus(channel, voltage):
    xController = pc.MDT693B(channel)
    xController.setVoltage(voltage)