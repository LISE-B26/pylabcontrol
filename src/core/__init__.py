# some usefull superclasses for the PythonLab project
import sip
sip.setapi('QVariant', 2)# set to version to so that the gui returns QString objects and not generic QVariants
from parameter import Parameter
from instruments import Instrument
from scripts import Script
from qt_b26_widgets import B26QTreeItem

__all__ = ['Script', 'Instrument', 'Parameter', 'B26QTreeItem']


