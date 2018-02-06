# This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
# PyLabControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyLabControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.


from PyLabControl.src.gui import LoadDialog



class LoadDialogB26(LoadDialog):
    """
This class builds on the Loaddialog and adds more options for script iterators
    """
    def __init__(self, elements_type, elements_old={}, filename=''):
        super(LoadDialogB26, self).__init__(elements_type, elements_old=elements_old, filename=filename)
        self.cmb_looping_variable.addItems(['Iter NVs', 'Iter Pts'])




if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui

    app = QtGui.QApplication(sys.argv)
    # ex = LoadDialog(elements_type = 'instruments', elements_old=instuments, filename="Z:\Lab\Cantilever\Measurements\\__tmp\\test.b26")
    # ex = LoadDialog(elements_type='scripts', elements_old=instuments)
    ex = LoadDialogB26(elements_type='scripts')

    ex.show()
    ex.raise_()

    print('asda')
    if ex.exec_():
        values = ex.getValues()
        print(values)

    sys.exit(app.exec_())

#
# if __name__ == '__main__':
#     from PyQt4 import QtGui
#     import sys
#
#     app = QtGui.QApplication(sys.argv)
#
#     dialog = LoadDialogB26(elements_type="scripts")
#
#     app.setWindowIcon(QtGui.QIcon('magnet_and_nv.ico'))
#
#     dialog.show()
#     dialog.raise_()
#     sys.exit(app.exec_())
#
#
#     print('-----', dialog.vars() )
#
#     if dialog.exec_():
#         xx = str(dialog.txt_probe_log_path.text())
#     scripts = dialog.getValues()
#
#     print('asdsadadas', xx)