# some usefull superclasses for the PythonLab project
#Qvariant only need for gui

try:
    __IPYTHON__
except NameError:
    import sip
    sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants

from parameter import Parameter
from instruments import Instrument
from scripts import Script, QThreadWrapper
from probe import Probe
from loading import load_probes, load_scripts, load_instruments
from qt_b26_widgets import B26QTreeItem
try:
    from read_probes import ReadProbes
except:
    pass
__all__ = ['Instrument', 'Parameter']


