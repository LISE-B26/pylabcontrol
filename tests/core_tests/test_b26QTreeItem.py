from unittest import TestCase
from PyQt4 import QtCore, QtGui
import sys
from src.core.qt_widgets import B26QTreeItem, B26QTreeWidget
from src.core import Parameter


class TestB26QTreeItem(TestCase):

    def test_create_widget(self):
        app = QtGui.QApplication(sys.argv)
        gui = QtGui.QMainWindow()
        centralwidget = QtGui.QWidget(gui)
        treeWidget = QtGui.QTreeWidget(centralwidget)


        p = Parameter('test', 0, int, 'info')

        item = B26QTreeItem( treeWidget, 'test', p['test'], p.valid_values['test'], p.info)


class TestB26QTreeWidget(TestCase):
    def test_create_widget(self):
        app = QtGui.QApplication(sys.argv)
        gui = QtGui.QMainWindow()
        centralwidget = QtGui.QWidget(gui)

        parameters = Parameter([
            Parameter('test1', 0, int, 'test parameter (int)'),
            Parameter('test2' ,
                      [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                       Parameter('test2_2', 0.0, float, 'test parameter (float)')
                       ])
        ])


        # for key, value in parameters.iteritems():
        #     print(key, value, parameters.valid_values[key], parameters.info[key])

        # QtGui.QTreeWidget(centralwidget)
        B26QTreeWidget(centralwidget, parameters)

