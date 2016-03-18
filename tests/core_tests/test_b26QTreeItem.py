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

        treeWidget = B26QTreeWidget(centralwidget, parameters)

