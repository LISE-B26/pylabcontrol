# some usefull superclasses for the PythonLab project
#Qvariant only need for gui

try:
    import sip
    sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
except ValueError:
    pass

from parameter import Parameter
from instruments import Instrument
from probe import Probe
from scripts import Script, QThreadWrapper
from qt_b26_load_dialog import LoadDialog
from loading import instantiate_probes, instantiate_scripts, instantiate_instruments
from qt_b26_widgets import B26QTreeItem
try:
    from read_probes import ReadProbes
except:
    pass
__all__ = ['Instrument', 'Parameter']


