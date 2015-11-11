__author__ = 'Experiment'


from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Extends the matplotlib backend FigureCanvas. A canvas for matplotlib figures with a constructed axis that is
# auto-expanding
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a Fi   gureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, autoscale_on=False)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class FileBoxOpen(QtGui.QLineEdit):
    def focusInEvent(self, QFocusEvent):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.setText(fname.getExistingDirectory(self, "Select Directory"))

class FileBoxSave(QtGui.QLineEdit):
    def __init__(self, default_path):
        QtGui.QLineEdit.__init__(self)
        self.default_path = default_path
        self.file_dialog_open = False
    def focusInEvent(self, QFocusEvent):
        if not self.file_dialog_open:
            self.file_dialog_open = True
            name = QtGui.QFileDialog.getExistingDirectory(self, 'Select a folder:', self.default_path, QtGui.QFileDialog.ShowDirsOnly)
            self.setText(name)
            self.window().setFocus()
            self.file_dialog_open = False

