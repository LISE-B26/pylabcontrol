"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell


    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.

"""

# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'load_dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!



from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(857, 523)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(509, 476, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 436, 841, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(1, 4, -1, 4)
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tree_infile = QtGui.QTreeView(Dialog)
        self.tree_infile.setGeometry(QtCore.QRect(270, 30, 256, 261))
        self.tree_infile.setDragEnabled(True)
        self.tree_infile.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.tree_infile.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.tree_infile.setUniformRowHeights(True)
        self.tree_infile.setObjectName(_fromUtf8("tree_infile"))
        self.tree_loaded = QtGui.QTreeView(Dialog)
        self.tree_loaded.setGeometry(QtCore.QRect(10, 30, 256, 261))
        self.tree_loaded.setFrameShape(QtGui.QFrame.StyledPanel)
        self.tree_loaded.setFrameShadow(QtGui.QFrame.Sunken)
        self.tree_loaded.setDragEnabled(True)
        self.tree_loaded.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.tree_loaded.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.tree_loaded.setObjectName(_fromUtf8("tree_loaded"))
        self.lbl_info = QtGui.QLabel(Dialog)
        self.lbl_info.setGeometry(QtCore.QRect(540, 30, 311, 261))
        self.lbl_info.setFrameShape(QtGui.QFrame.Box)
        self.lbl_info.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setObjectName(_fromUtf8("lbl_info"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 241, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(280, 10, 241, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btn_open = QtGui.QPushButton(Dialog)
        self.btn_open.setGeometry(QtCore.QRect(774, 440, 75, 23))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_open.sizePolicy().hasHeightForWidth())
        self.btn_open.setSizePolicy(sizePolicy)
        self.btn_open.setObjectName(_fromUtf8("btn_open"))
        self.lbl_probe_log_path = QtGui.QLabel(Dialog)
        self.lbl_probe_log_path.setGeometry(QtCore.QRect(10, 440, 22, 23))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_probe_log_path.sizePolicy().hasHeightForWidth())
        self.lbl_probe_log_path.setSizePolicy(sizePolicy)
        self.lbl_probe_log_path.setObjectName(_fromUtf8("lbl_probe_log_path"))
        self.txt_probe_log_path = QtGui.QLineEdit(Dialog)
        self.txt_probe_log_path.setGeometry(QtCore.QRect(39, 440, 728, 23))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txt_probe_log_path.sizePolicy().hasHeightForWidth())
        self.txt_probe_log_path.setSizePolicy(sizePolicy)
        self.txt_probe_log_path.setObjectName(_fromUtf8("txt_probe_log_path"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 290, 241, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.tree_script_sequence = QtGui.QTreeView(Dialog)
        self.tree_script_sequence.setGeometry(QtCore.QRect(10, 310, 261, 121))
        self.tree_script_sequence.setDragEnabled(True)
        self.tree_script_sequence.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.tree_script_sequence.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.tree_script_sequence.setObjectName(_fromUtf8("tree_script_sequence"))
        self.btn_script_sequence = QtGui.QPushButton(Dialog)
        self.btn_script_sequence.setGeometry(QtCore.QRect(280, 380, 111, 41))
        self.btn_script_sequence.setObjectName(_fromUtf8("btn_script_sequence"))
        self.cmb_looping_variable = QtGui.QComboBox(Dialog)
        self.cmb_looping_variable.setGeometry(QtCore.QRect(280, 350, 111, 22))
        self.cmb_looping_variable.setObjectName(_fromUtf8("cmb_looping_variable"))
        self.textEdit = QtGui.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(540, 300, 301, 131))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.txt_script_sequence_name = QtGui.QLineEdit(Dialog)
        self.txt_script_sequence_name.setGeometry(QtCore.QRect(280, 320, 113, 20))
        self.txt_script_sequence_name.setObjectName(_fromUtf8("txt_script_sequence_name"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Loading...", None))
        self.lbl_info.setText(_translate("Dialog", "info", None))
        self.label.setText(_translate("Dialog", "Selected", None))
        self.label_2.setText(_translate("Dialog", "Not Selected", None))
        self.btn_open.setText(_translate("Dialog", "open", None))
        self.lbl_probe_log_path.setText(_translate("Dialog", "Path", None))
        self.txt_probe_log_path.setText(_translate("Dialog", "Z:\\Lab\\Cantilever\\Measurements", None))
        self.label_3.setText(_translate("Dialog", "Script Sequence", None))
        self.btn_script_sequence.setText(_translate("Dialog", "Add Script Sequence", None))
        self.textEdit.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Enter docstring here</span></p></body></html>", None))
        self.txt_script_sequence_name.setText(_translate("Dialog", "DefaultName", None))

