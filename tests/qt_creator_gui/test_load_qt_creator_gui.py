from PyQt4 import QtGui
from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('../../src/qt_creator_gui/zi_control.ui') # with this we don't have to convert the .ui file into a python file!

import datetime
from collections import deque
# from src.qt_creator_gui import QTreeInstrument, QTreeScript, QTreeParameter


class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # link slider to functions
            #
            # self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            # self.sliderPosition.valueChanged.connect(lambda: self.set_position())




            # link buttons to functions
            self.btn_start_script.clicked.connect(lambda: self.btn_clicked())
            self.btn_stop_script.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record.clicked.connect(lambda: self.btn_clicked())
            # self.btn_start_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_save_to_disk.clicked.connect(lambda: self.btn_clicked())
            #
            # self.btn_plus.clicked.connect(lambda: self.set_position())
            # self.btn_minus.clicked.connect(lambda: self.set_position())
            # self.btn_center.clicked.connect(lambda: self.set_position())
            # self.btn_to_zero.clicked.connect(lambda: self.set_position())



            # link checkboxes to functions
            # self.checkIRon.stateChanged.connect(lambda: self.control_light())
            # self.checkGreenon.stateChanged.connect(lambda: self.control_light())
            # self.checkWhiteLighton.stateChanged.connect(lambda: self.control_light())
            # self.checkCameraon.stateChanged.connect(lambda: self.control_light())
            # self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

            # link combo box
            # self.cmb_filterwheel.addItems(self._settings['hardware']['parameters_filterwheel']['position_list'].keys())
            # self.cmb_filterwheel.currentIndexChanged.connect(lambda: self.control_light())

            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))
            self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))


            for script in self.scripts:
                if isinstance(script, QtScript):
                    print(script.name)
                    script.updateProgress.connect(self.update_progress)

        # define data container
        self.past_commands = deque() # history of executed commands

        # define instrument_tests
        maestro = MaestroController('maestro 6 channels')
        self.instruments = [
            ZIHF2('ZiHF2'),
            # Maestro_BeamBlock(maestro,'IR beam block', {'channel':4})
            MaestroBeamBlock(maestro,'IR beam block')
        ]
        #
        # # define parameters to monitor
        # zi_inst = get_elemet('ZiHF2', self.instrument_tests)
        # self.monitor_parameters = [
        #     {'target' : zi_inst, 'parameter' : get_elemet('freq', zi_inst.parameters)}
        # ]

        # define scripts_old
        self.scripts = [
            Script_Dummy('script dummy 1'),
            QtScript('threaded script')
        ]

        # fill the trees
        self.fill_treewidget(self.tree_scripts)
        self.tree_scripts.setColumnWidth(0,200)

        self.fill_treewidget(self.tree_settings)
        self.tree_settings.setColumnWidth(0,200)

        # self.fill_treewidget(self.tree_monitor)
        # self.tree_monitor.setColumnWidth(0,200)

        connect_controls()


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = ControlMainWindow()
    ex.show()
    sys.exit(app.exec_())