__author__ = 'Experiment'

from matplotlib.widgets import RectangleSelector
import gui_custom_widgets as gui_cw
from PyQt4 import QtGui


def addScan(self, vbox_main, plotBox):

    self.imPlot = gui_cw.MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)

    """
    self.xVoltageMin = QtGui.QLineEdit(self.main_widget)
    self.yVoltageMin = QtGui.QLineEdit(self.main_widget)
    self.xVoltageMax = QtGui.QLineEdit(self.main_widget)
    self.yVoltageMax = QtGui.QLineEdit(self.main_widget)
    self.xPts = QtGui.QLineEdit(self.main_widget)
    self.yPts = QtGui.QLineEdit(self.main_widget)
    self.timePerPt = QtGui.QLineEdit(self.main_widget)
    self.xVoltage = QtGui.QLineEdit(self.main_widget)
    self.yVoltage = QtGui.QLineEdit(self.main_widget)
    self.xVoltageMinL = QtGui.QLabel(self.main_widget)
    self.xVoltageMinL.setText("xVoltsMin:")
    self.yVoltageMinL = QtGui.QLabel(self.main_widget)
    self.yVoltageMinL.setText("yVoltsMin:")
    self.xVoltageMaxL = QtGui.QLabel(self.main_widget)
    self.xVoltageMaxL.setText("xVoltsMax:")
    self.yVoltageMaxL = QtGui.QLabel(self.main_widget)
    self.yVoltageMaxL.setText("yVoltsMax:")
    self.xVoltageL = QtGui.QLabel(self.main_widget)
    self.xVoltageL.setText("xVolts:")
    self.yVoltageL = QtGui.QLabel(self.main_widget)
    self.yVoltageL.setText("yVolts:")
    self.xPtsL = QtGui.QLabel(self.main_widget)
    self.xPtsL.setText("Number of x Points:")
    self.yPtsL = QtGui.QLabel(self.main_widget)
    self.yPtsL.setText("Number of Y Points:")
    self.timePerPtL = QtGui.QLabel(self.main_widget)
    self.timePerPtL.setText("Timer Per Point:")

    self.saveLocImage = QtGui.QLineEdit(self.main_widget)
    self.saveLocImage.setText('Z:\\Lab\\Cantilever\\Measurements\\Images')
    self.saveLocImageL = QtGui.QLabel(self.main_widget)
    self.saveLocImageL.setText("Image Location")
    self.saveTagImage = QtGui.QLineEdit(self.main_widget)
    self.saveTagImage.setText('Image')
    self.saveTagImageL = QtGui.QLabel(self.main_widget)
    self.saveTagImageL.setText("Tag")

    self.buttonVSet = QtGui.QPushButton('Set Voltage', self.main_widget)
    self.buttonVSet.clicked.connect(self.vSetBtnClicked)

    self.buttonSaveImage = QtGui.QPushButton('Save Image', self.main_widget)
    self.buttonSaveImage.clicked.connect(self.saveImageClicked)
    self.buttonLoadDefaulScanRange = QtGui.QPushButton('Large Scan', self.main_widget)
    self.buttonLoadDefaulScanRange.clicked.connect(self.largeScanButtonClicked)



    self.autosaveCheck = QtGui.QCheckBox('AutoSave',self.main_widget)
    self.autosaveCheck.setChecked(True)

    self.buttonRedrawLaser = QtGui.QPushButton('Redraw laser spot',self.main_widget)
    self.buttonRedrawLaser.clicked.connect(self.drawDot_RoI)
    self.buttonLoadScanRange = QtGui.QPushButton('Load scan range',self.main_widget)
    self.buttonLoadScanRange.clicked.connect(lambda: self.loadRoI())

    self.buttonAutofocusRoI = QtGui.QPushButton('auto focus (RoI)',self.main_widget)
    self.buttonAutofocusRoI.clicked.connect(self.autofcus_RoI)

    self.zPosL = QtGui.QLabel(self.main_widget)
    self.zPosL.setText("focus (V)")
    self.zPos = QtGui.QLineEdit(self.main_widget)
    self.zRangeL = QtGui.QLabel(self.main_widget)
    self.zRangeL.setText('range auto focus (V)')
    self.zRange = QtGui.QLineEdit(self.main_widget)
    self.zPtsL = QtGui.QLabel(self.main_widget)
    self.zPtsL.setText('pts auto focus (z)')
    self.zPts = QtGui.QLineEdit(self.main_widget)
    self.xyRange = QtGui.QLineEdit(self.main_widget)
    self.xyRangeL = QtGui.QLabel(self.main_widget)
    self.xyRangeL.setText('pts focus range (xy)')

    self.buttonESRSequence = QtGui.QPushButton("Choose NVs", self.main_widget)
    self.buttonESRFinished = QtGui.QPushButton("FinishedChoosing", self.main_widget)
    self.esrSaveLocL = QtGui.QLabel(self.main_widget)
    self.esrSaveLocL.setText("ESR Save Location")
    self.esrSaveLoc = FileBox(self.main_widget)
    self.esrSaveLoc.setText('Z:\\Lab\\Cantilever\\Measurements')
    self.esrReadLocL = QtGui.QLabel(self.main_widget)
    self.esrReadLocL.setText("ESR Read Location")
    self.esrReadLoc = QtGui.QLineEdit(self.main_widget)
    self.buttonESRRun = QtGui.QPushButton("Run ESR", self.main_widget)
    self.errSquare = QtGui.QFrame(self.main_widget)
    self.errSquare.setGeometry(150, 20, 100, 100)
    self.errSquare.setStyleSheet("QWidget { background-color: %s }" % 'Green')
    self.errSquareMsg = QtGui.QLineEdit(self.main_widget)


    #set initial values for scan values
    # self.loadRoI('Z://Lab//Cantilever//Measurements//default_settings.config')
    self.loadSettings('Z://Lab//Cantilever//Measurements//default_settings.config')



    plotBox.addWidget(self.imPlot)
    self.scanLayout = QtGui.QGridLayout()


    # Scan area
    self.scanLayout.addWidget(self.xVoltageMin, 2,1)
    self.scanLayout.addWidget(self.yVoltageMin, 2,2)
    self.scanLayout.addWidget(self.xVoltageMinL,1,1)
    self.scanLayout.addWidget(self.yVoltageMinL,1,2)
    self.scanLayout.addWidget(self.xVoltageMax, 2,3)
    self.scanLayout.addWidget(self.yVoltageMax, 2,4)
    self.scanLayout.addWidget(self.xVoltageMaxL,1,3)
    self.scanLayout.addWidget(self.yVoltageMaxL,1,4)
    self.scanLayout.addWidget(self.xPts,2,5)
    self.scanLayout.addWidget(self.xPtsL,1,5)
    self.scanLayout.addWidget(self.yPts, 2,6)
    self.scanLayout.addWidget(self.yPtsL, 1,6)
    self.scanLayout.addWidget(self.timePerPt,2,7)
    self.scanLayout.addWidget(self.timePerPtL,1,7)
    self.scanLayout.addWidget(self.buttonLoadScanRange,6,14)
    self.scanLayout.addWidget(self.buttonLoadDefaulScanRange,2,8)
    # execute commands



    # laser position
    self.scanLayout.addWidget(self.xVoltageL,1,9)
    self.scanLayout.addWidget(self.xVoltage, 2,9)
    self.scanLayout.addWidget(self.yVoltageL,1,10)
    self.scanLayout.addWidget(self.yVoltage, 2,10)
    self.scanLayout.addWidget(self.buttonRedrawLaser,3,9)
    self.scanLayout.addWidget(self.buttonVSet,3,10)


    # save image
    self.scanLayout.addWidget(self.saveLocImageL,6,1)
    self.scanLayout.addWidget(self.saveLocImage,6,2,1,4)

    self.scanLayout.addWidget(self.saveTagImageL,6,6)
    self.scanLayout.addWidget(self.saveTagImage,6,7)

    self.scanLayout.addWidget(self.buttonSaveImage,6,8)
    self.scanLayout.addWidget(self.autosaveCheck,6,9)







    # autofocus settings
    self.scanLayout.addWidget(self.xyRangeL,3,12)
    self.scanLayout.addWidget(self.xyRange,4,12)
    self.scanLayout.addWidget(self.zPosL,3,13)
    self.scanLayout.addWidget(self.zPos,4,13)
    self.scanLayout.addWidget(self.zRangeL,3,14)
    self.scanLayout.addWidget(self.zRange,4,14)
    self.scanLayout.addWidget(self.zPtsL,3,15)
    self.scanLayout.addWidget(self.zPts,4,15)
    self.scanLayout.addWidget(self.buttonAutofocusRoI,3,16)

    self.scanLayout.addWidget(self.buttonESRSequence,5,1)
    self.scanLayout.addWidget(self.buttonESRFinished,5,2)
    self.scanLayout.addWidget(self.esrSaveLocL,5,3)
    self.scanLayout.addWidget(self.esrSaveLoc,5,4)
    self.scanLayout.addWidget(self.buttonESRRun,5,5)
    self.scanLayout.addWidget(self.esrReadLocL,5,6)
    self.scanLayout.addWidget(self.esrReadLoc,5,7)
    self.buttonESRSequence.clicked.connect(self.start_esr_sequence)
    self.buttonESRFinished.clicked.connect(self.finished_choosing)
    self.buttonESRRun.clicked.connect(self.run_esr)
    self.esr_running = False

    vbox.addLayout(self.scanLayout)
    #self.imageData = None
    self.imageData = numpy.array(pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-27_18-41-56-NVBaselineTests.csv"))
    self.imPlot.axes.imshow(self.imageData, extent = [-.05,.05,-.05,.05])
    self.imPlot.draw()

    self.mouseNVImageConnect = self.imPlot.mpl_connect('button_press_event', self.mouseNVImage)
    rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
    self.RS = RectangleSelector(self.imPlot.axes, self.select_RoI, button = 3, drawtype='box', rectprops = rectprops)


    # add button to execute script
    self.button_exec_script = QtGui.QPushButton('run script', self.main_widget)
    self.button_exec_script.clicked.connect(self.exec_scriptBtnClicked)
    self.scanLayout.addWidget(self.button_exec_script,6,16)

    # add button to execute script
    self.button_save_set = QtGui.QPushButton('save set', self.main_widget)
    self.button_save_set.clicked.connect(lambda: self.save_settings())
    self.scanLayout.addWidget(self.button_save_set,6,15)
    """

    ##### GRID IMAGE ############################################################################################
    ################################################################################################################




    ##### GRID CONTROLS ############################################################################################
    ################################################################################################################

    self.grid_controls = QtGui.QGridLayout()
    vbox_main.addLayout(self.grid_controls)





    ##### settings #################################################################################################
    self.group_settings = QtGui.QGroupBox("Settings")
    self.grid_settings = QtGui.QGridLayout()
    self.grid_controls.addWidget(self.group_settings,1,1)
    self.group_settings.setLayout(self.grid_settings)


    row_start = 1
    column_start =  1

    self.label_scan_1a = QtGui.QLabel("pt 1a (scan)", self.main_widget)
    self.grid_settings.addWidget(self.label_scan_1a,row_start,column_start)
    self.label_scan_1b = QtGui.QLabel("pt 1b (scan)", self.main_widget)
    self.grid_settings.addWidget(self.label_scan_1b,row_start+1,column_start)
    self.button_scan_2a = QtGui.QPushButton('pt 2a', self.main_widget)
    self.grid_settings.addWidget(self.button_scan_2a,row_start+2,column_start)
    self.button_scan_2b = QtGui.QPushButton('pt 2b', self.main_widget)
    self.grid_settings.addWidget(self.button_scan_2b,row_start+3,column_start)

    self.label_x = QtGui.QLabel("x", self.main_widget)
    self.grid_settings.addWidget(self.label_x,row_start-1,column_start+1)
    self.txt_pt_1a_x = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1a_x,row_start,column_start+1)
    self.txt_pt_1b_x = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1b_x,row_start+1,column_start+1)
    self.txt_pt_2a_x = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2a_x,row_start+2,column_start+1)
    self.txt_pt_2b_x = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2b_x,row_start+3,column_start+1)

    self.label_y = QtGui.QLabel("y", self.main_widget)
    self.grid_settings.addWidget(self.label_y,row_start-1,column_start+2)
    self.txt_pt_1a_y = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1a_y,row_start,column_start+2)
    self.txt_pt_1b_y = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1b_y,row_start+1,column_start+2)
    self.txt_pt_2a_y = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2a_y,row_start+2,column_start+2)
    self.txt_pt_2b_y = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2b_y,row_start+3,column_start+2)

    self.label_pts = QtGui.QLabel("pts", self.main_widget)
    self.grid_settings.addWidget(self.label_pts,row_start-1,column_start+3)
    self.txt_pt_1a_pts = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1a_pts,row_start,column_start+3)
    self.txt_pt_1b_pts = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_1b_pts,row_start+1,column_start+3)
    self.txt_pt_2a_pts = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2a_pts,row_start+2,column_start+3)
    self.txt_pt_2b_pts = QtGui.QLineEdit(self.main_widget)
    self.grid_settings.addWidget(self.txt_pt_2b_pts,row_start+3,column_start+3)


    self.button_set_laser = QtGui.QPushButton('set laser', self.main_widget)
    self.grid_settings.addWidget(self.button_set_laser,row_start+2,column_start+4)


    ##### display #################################################################################################
    self.group_display = QtGui.QGroupBox("Display")
    self.group_display.isCheckable()
    self.grid_display = QtGui.QGridLayout()
    self.grid_controls.addWidget(self.group_display,1,2)
    self.group_display.setLayout(self.grid_display)

    row_start = 1
    column_start =  1

    self.radio_roi = QtGui.QCheckBox("&region of interest (RoI)")
    self.grid_display.addWidget(self.radio_roi,row_start, column_start)
    self.radio_grid = QtGui.QRadioButton("Grid")
    self.grid_display.addWidget(self.radio_grid,row_start +1, column_start)
    self.radio_line = QtGui.QRadioButton("Line")
    self.grid_display.addWidget(self.radio_line,row_start +2, column_start)
    self.radio_laser = QtGui.QCheckBox("Laser (pt A)")
    self.grid_display.addWidget(self.radio_laser,row_start +3, column_start)


    # set RoI and zoom
    self.button_zoom_in_RoI = QtGui.QPushButton('zoom in (RoI)',self.main_widget)
    self.button_zoom_in_RoI.clicked.connect(self.zoom_RoI)
    self.grid_display.addWidget(self.button_zoom_in_RoI,row_start,column_start+1)
    self.button_zoom_out_RoI = QtGui.QPushButton('zoom out', self.main_widget)
    self.button_zoom_out_RoI.clicked.connect(self.imageHomeClicked)
    self.grid_display.addWidget(self.button_zoom_out_RoI,row_start,column_start+2)

    # colar bar
    self.cbar_max = QtGui.QLineEdit(self.main_widget)
    self.grid_display.addWidget(self.cbar_max,row_start +5, column_start)
    self.label_cbar_max = QtGui.QLabel("Colorbar Threshold", self.main_widget)
    self.grid_display.addWidget(self.label_cbar_max,row_start +5, column_start +1)
    self.button_cbar_thresh = QtGui.QPushButton('Update Colorbar', self.main_widget)
    self.button_cbar_thresh.clicked.connect(self.cbarThreshClicked)
    self.grid_display.addWidget(self.button_cbar_thresh,row_start +5, column_start +2)

    self.button_stop = QtGui.QPushButton('Stop Scan', self.main_widget)
    self.button_stop.clicked.connect(self.stopButtonClicked)
    self.grid_display.addWidget(self.button_stop,row_start +6,column_start)
    self.button_scan = QtGui.QPushButton('Scan', self.main_widget)
    self.button_scan.clicked.connect(self.scanBtnClicked)
    self.grid_display.addWidget(self.button_scan,row_start +6,column_start+1)



    ##### execute #################################################################################################
    self.group_execute = QtGui.QGroupBox("Execute")
    self.grid_execute = QtGui.QGridLayout()
    self.grid_controls.addWidget(self.group_execute,2,1)
    self.group_execute.setLayout(self.grid_execute)

    row_start = 1
    column_start =  1

    self.label_execute = QtGui.QLabel('execute', self.main_widget)
    self.grid_execute.addWidget(self.label_execute,row_start,column_start)
    self.cmb_execute = QtGui.QComboBox(self.main_widget)
    self.cmb_execute.addItems(['RoI', 'Grid', 'Line', 'Laser (pt A)', 'None'])
    self.cmb_execute.activated.connect(self.visualize_2pt_disp)
    self.grid_execute.addWidget(self.cmb_execute,row_start+1,column_start)

    self.label_settings = QtGui.QLabel('script settings', self.main_widget)
    self.grid_execute.addWidget(self.label_settings,row_start,column_start+1)
    self.path_script = QtGui.QLineEdit(self.main_widget)
    self.path_script.setText('Z:\\Lab\\Cantilever\\Measurements')
    self.grid_execute.addWidget(self.path_script,row_start+1,column_start+1)

    self.button_execute_script = QtGui.QPushButton('run script', self.main_widget)
    self.grid_execute.addWidget(self.button_execute_script,row_start+1,column_start+2)


    self.group_execute = QtGui.QGroupBox("Execute")
    self.grid_execute = QtGui.QGridLayout()
    self.grid_controls.addWidget(self.group_execute,2,1)
    self.group_execute.setLayout(self.grid_execute)

    ##### global #################################################################################################
    self.group_global = QtGui.QGroupBox("global")
    self.grid_global = QtGui.QGridLayout()
    self.grid_controls.addWidget(self.group_global,2,2)
    self.group_global.setLayout(self.grid_global)

    row_start = 1
    column_start =  1

    self.button_load_settings = QtGui.QPushButton('load settings', self.main_widget)
    self.grid_global.addWidget(self.button_load_settings,row_start,column_start)

    self.button_save_settings = QtGui.QPushButton('load settings', self.main_widget)
    self.grid_global.addWidget(self.button_save_settings,row_start,column_start+1)
    self.button_exit = QtGui.QPushButton('exit', self.main_widget)
    self.grid_global.addWidget(self.button_exit,row_start,column_start+2)

    # settings
    self.button_APD = QtGui.QPushButton('Use APD',self.main_widget)
    self.button_APD.setCheckable(True)
    self.button_APD.setChecked(True)
    # self.button_APD.clicked.connect(self.button_APD)
    self.grid_global.addWidget(self.button_APD,1,16)


    """
    self.circ = None # marker for laser
    self.rect = None # marker for RoI

    self.queue = Queue.Queue()

    self.timer = QtCore.QTimer()
    self.timer.start(5000)



    self.timer.timeout.connect(self.checkValidImage)

    self.scanLayout.addWidget(self.errSquare, 7,1)
    self.scanLayout.addWidget(self.errSquareMsg, 7,2,1,4)

    self.laserPos = None
    self.imageRoI = {
        "dx": .8,
        "dy": .8,
        "xPts": 120,
        "xo": 0,
        "yPts": 120,
        "yo": 0
    }
    QtGui.QApplication.processEvents()
        """