import hardware_modules.PiezoController as pc

def set_focus(channel, voltage):
    xController = pc.MDT693B(channel)
    xController.setVoltage(voltage)