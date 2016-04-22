# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'load_dialog.ui'
#
# Created: Fri Apr 22 14:53:04 2016
#      by: PyQt4 UI code generator 4.10.4
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
        Dialog.resize(857, 392)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(510, 350, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 310, 841, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lbl_probe_log_path = QtGui.QLabel(self.horizontalLayoutWidget)
        self.lbl_probe_log_path.setObjectName(_fromUtf8("lbl_probe_log_path"))
        self.horizontalLayout.addWidget(self.lbl_probe_log_path)
        self.txt_probe_log_path = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.txt_probe_log_path.setObjectName(_fromUtf8("txt_probe_log_path"))
        self.horizontalLayout.addWidget(self.txt_probe_log_path)
        self.btn_open = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.btn_open.setObjectName(_fromUtf8("btn_open"))
        self.horizontalLayout.addWidget(self.btn_open)
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

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Loading...", None))
        self.lbl_probe_log_path.setText(_translate("Dialog", "Path", None))
        self.txt_probe_log_path.setText(_translate("Dialog", "Z:\\Lab\\Cantilever\\Measurements", None))
        self.btn_open.setText(_translate("Dialog", "open", None))
        self.lbl_info.setText(_translate("Dialog", "info", None))
        self.label.setText(_translate("Dialog", "Selected", None))
        self.label_2.setText(_translate("Dialog", "Not Selected", None))

