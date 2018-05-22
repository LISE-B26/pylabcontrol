
# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.


# import sip
from unittest import TestCase
# sip.setapi('QVariant', 2)
from PyQt5 import QtGui
import sys
from src.core import Parameter

class UI(QtGui.QMainWindow):

    def __init__(self, parameters = None, parent=None):

        ## Init:
        super(UI, self).__init__( parent )

        # ----------------
        # Create Simple UI with QTreeWidget
        # ----------------
        self.centralwidget = QtGui.QWidget(self)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)

        self.parameters = parameters



        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.verticalLayout.addWidget(self.treeWidget)
        self.setCentralWidget(self.centralwidget)
        fill_tree(self.treeWidget, self.parameters)
        # ----------------
        # Set TreeWidget Headers
        # ----------------
        HEADERS = ( "parameter", "value" )
        self.treeWidget.setColumnCount( len(HEADERS) )
        self.treeWidget.setHeaderLabels( HEADERS )


        # ----------------
        # Add Custom QTreeWidgetItem
        # ----------------
        self.treeWidget.itemChanged.connect(lambda: self.update_parameters(self.treeWidget, self.parameters))

        # shot down
        print('close')
        self.close()

class TestB26QTreeWidget(TestCase):
    def test_create_widget_parameters(self):


        parameters = Parameter([
            Parameter('test1', 0, int, 'test parameter (int)'),
            Parameter('test2' ,
                      [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                       Parameter('test2_2', 0.0, float, 'test parameter (float)'),
                       Parameter('test2_3', 'a', ['a', 'b', 'c'], 'test parameter (list)'),
                       Parameter('test2_4', False, bool, 'test parameter (bool)')
                       ]),
            Parameter('test3', 'aa', ['aa', 'bb', 'cc'], 'test parameter (list)'),
            Parameter('test4', False, bool, 'test parameter (bool)')
        ])

        app = QtGui.QApplication(sys.argv)
        ex = UI(parameters)
        # sys.exit(app.exec_())



    def test_create_widget_parameters(self):


        parameters = {
            'test1':0,
            'test2':{'test2_1':'ss', 'test3':4},
            'test4':0
        }

        app = QtGui.QApplication(sys.argv)
        ex = UI(parameters)
        # sys.exit(app.exec_())
