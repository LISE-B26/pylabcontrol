# some usefull superclasses for the PythonLab project
#Qvariant only need for gui

# try:
#     import sip
#     sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
# except ValueError:
#     pass

from PyLabControl.src.core.instruments import Instrument
from PyLabControl.src.core.parameter import Parameter
from PyLabControl.src.core.probe import Probe
from PyLabControl.src.core.scripts import Script
from PyLabControl.src.core.script_iterator import ScriptIterator
try:
    from read_probes import ReadProbes
except:
    pass
# try:
#     from PyLabControl.src.core.script_sequence import ScriptIterator
# except:
#     pass

__all__ = ['Instrument', 'Parameter']