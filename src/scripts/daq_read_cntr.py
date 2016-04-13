from src.core.scripts import Script
from PySide.QtCore import Signal, QThread

from src.old_hardware_modules import APD as APDIn

# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time
import pandas as pd
from PyQt4 import QtGui


class Daq_Read_Cntr(Script, QThread):
    raise NotImplementedError