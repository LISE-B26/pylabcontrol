from src.instruments import microwave_generator
from src.core.scripts import Script

from src.old_hardware_modules import APD as APDIn

# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time
import pandas as pd
from PyQt4 import QtGui


class ESR(Script):
    raise NotImplementedError