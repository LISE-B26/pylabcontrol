#!/usr/bin/python

# Import PySide classes
import sys
# from PySide.QtCore import *
# from PySide.QtGui import *

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

# Create a Qt application
app = QtGui.QApplication(sys.argv)
# Create a Label and show it
label = QtGui.QLabel("<font color=red size=40>Hello World</font>")
label = QtGui.QPushButton("<font color=red size=40>Hello World</font>")
label.show()
# Enter Qt application main loop
app.exec_()
sys.exit()




# # -*- coding: utf-8 -*-
#
# """
# ZetCode PyQt4 tutorial
#
# In this example, we create a bit
# more complicated window layout using
# the QtGui.QGridLayout manager.
#
# author: Jan Bodnar
# website: zetcode.com
# last edited: October 2011
# """
#
# import sys
# from PyQt4 import QtGui
#
#
# class GUI_FPGA(QtGui.QWidget):
#
#     def __init__(self):
#         super(GUI_FPGA, self).__init__()
#
#         self.initUI()
#
#     def initUI(self):
#
#         title = QtGui.QLabel('Title')
#         author = QtGui.QLabel('Author')
#         review = QtGui.QLabel('Review')
#
#         titleEdit = QtGui.QLineEdit()
#         authorEdit = QtGui.QLineEdit()
#         reviewEdit = QtGui.QTextEdit()
#
#         grid = QtGui.QGridLayout()
#         grid.setSpacing(10)
#
#         grid.addWidget(title, 1, 0)
#         grid.addWidget(titleEdit, 1, 1)
#
#         grid.addWidget(author, 2, 0)
#         grid.addWidget(authorEdit, 2, 1)
#
#         grid.addWidget(review, 3, 0)
#         grid.addWidget(reviewEdit, 3, 1, 5, 1)
#
#         self.setLayout(grid)
#
#         self.setGeometry(300, 300, 350, 300)
#         self.setWindowTitle('Review')
#         self.show()
#
# def main():
#
#     app = QtGui.QApplication(sys.argv)
#     ex = GUI_FPGA()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()