__author__ = 'Experiment'

from matplotlib.widgets import RectangleSelector
import gui_custom_widgets as gui_cw
from PyQt4 import QtGui
import numpy as np
import pandas as pd
# import json as json
import Queue

import functions.ReadWriteCommands as rw
from gui import GuiDeviceTriggers as DeviceTriggers
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import functions.Meshing as Meshing
import scripts.ESR_many_NVs as ESR
import scripts.auto_focus as AF

def add_scan_layout(ApplicationWindow, vbox_main, plotBox):



    def display_shapes():


        remove_patches()

        # ApplicationWindow.imPlot.axes.imshow(ApplicationWindow.imageData, extent = [-.05,.05,-.05,.05])
        if ApplicationWindow.radio_roi.isChecked()==True:
            get_roi_patch()
        if ApplicationWindow.radio_grid.isChecked()==True:
            get_grid_patches()
        if ApplicationWindow.radio_line.isChecked()==True:
            get_line_patches()
        if ApplicationWindow.radio_laser.isChecked()==True:
            get_dot_patch_laser()
        if ApplicationWindow.radio_pt2.isChecked()==True:
            get_dot_patch_pt2()

        if(not ApplicationWindow.patches==[]):
            # ApplicationWindow.imPlot.axes.add_collection(ApplicationWindow.patches)
            for patch in ApplicationWindow.patches:
                ApplicationWindow.imPlot.axes.add_patch(patch)

        ApplicationWindow.imPlot.draw()
    def get_dot_patch_pt2():
        size, pt_a, _,_,_,_ = get_pts_and_size(ApplicationWindow)
        ApplicationWindow.patches.append(patches.Circle((pt_a[0], pt_a[1]), 2*size, fc = 'y'))

    def get_dot_patch_laser():
        size, _, _,_,_,pt_L = get_pts_and_size(ApplicationWindow)
        ApplicationWindow.patches.append(patches.Circle((pt_L[0], pt_L[1]), 3*size, fc = 'r'))

    def get_line_patches():
        size, pt_a, pt_b, xpts, _,_  = get_pts_and_size(ApplicationWindow)
        points = Meshing.get_points_along_line(pt_a, pt_b, xpts)

        for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'g') for pt in points]:
            ApplicationWindow.patches.append(patch)
    def get_grid_patches():
        size, pt_a, pt_b, xpts, ypts,_  = get_pts_and_size(ApplicationWindow)
        points = Meshing.get_points_on_a_grid(pt_a, pt_b, xpts, ypts)

        for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'w') for pt in points]:
            ApplicationWindow.patches.append(patch)
    def get_roi_patch():
        size, pt_a, pt_b ,_,_,_ = get_pts_and_size(ApplicationWindow)

        center, w, h = Meshing.two_pts_to_center_size(pt_a, pt_b)

        ApplicationWindow.patches.append(patches.Rectangle((center[0] - w /2., center[1] - h/2.),
                           width = w, height = h , fc = 'none' , ec = 'r'))
    def remove_patches():
        if(not ApplicationWindow.patches==[]):
            print  ApplicationWindow.patches
            for patch in ApplicationWindow.patches:
                patch.remove()
            ApplicationWindow.imPlot.draw()
        ApplicationWindow.patches=[]



    def set_laser(ptL = None):

        if ptL == None:
            xL = ApplicationWindow.txt_pt_2a_x.text()
            yL = ApplicationWindow.txt_pt_2a_y.text()
        else:
            xL = str(ptL[0])
            yL = str(ptL[1])

        ApplicationWindow.txt_pt_laser_x.setText(xL)
        ApplicationWindow.txt_pt_laser_y.setText(yL)
        DeviceTriggers.setDaqPt(float(xL), float(yL))

        display_shapes()

        ApplicationWindow.statusBar().showMessage("Galvo Position Updated",2000)

    ##################################################################################
    # ADD EXECUTE ####################################################################
    ##################################################################################
    def add_execute():
        row_start = 1
        column_start =  1

        ApplicationWindow.label_execute = QtGui.QLabel('execute', ApplicationWindow.main_widget)
        ApplicationWindow.grid_execute.addWidget(ApplicationWindow.label_execute,row_start,column_start)
        ApplicationWindow.cmb_execute = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_execute.addItems(['ESR (grid)', 'AutoFocus'])
        ApplicationWindow.cmb_execute.activated.connect(lambda: change_script(ApplicationWindow))
        ApplicationWindow.grid_execute.addWidget(ApplicationWindow.cmb_execute,row_start+1,column_start)

        ApplicationWindow.label_settings = QtGui.QLabel('script settings', ApplicationWindow.main_widget)
        ApplicationWindow.grid_execute.addWidget(ApplicationWindow.label_settings,row_start,column_start+1)
        ApplicationWindow.path_script = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.path_script.textChanged.connect(lambda: change_script_path(ApplicationWindow))
        # ApplicationWindow.path_script.setText('Z:\\Lab\\Cantilever\\Measurements')
        ApplicationWindow.grid_execute.addWidget(ApplicationWindow.path_script,row_start+1,column_start+1)

        ApplicationWindow.button_execute_script = QtGui.QPushButton('run script', ApplicationWindow.main_widget)
        ApplicationWindow.button_execute_script.clicked.connect(lambda: execute_script(ApplicationWindow))
        ApplicationWindow.grid_execute.addWidget(ApplicationWindow.button_execute_script,row_start+1,column_start+2)

        ApplicationWindow.parameters_paths_scripts = {
			"ESR": "ESR path_script",
			"AutoFocus": "AF path_script"
		}

        def change_script(ApplicationWindow):
            script_name = str(ApplicationWindow.cmb_execute.currentText())
            script_path = ApplicationWindow.parameters_paths_scripts[script_name]
            # ApplicationWindow.statusBar().showMessage(ApplicationWindow.cmb_execute.currentText(),1000)
            ApplicationWindow.path_script.setText(script_path)

        def change_script_path(ApplicationWindow):

            script_name = str(ApplicationWindow.cmb_execute.currentText())
            script_path = str(ApplicationWindow.path_script.text())

            ApplicationWindow.parameters_paths_scripts[script_name] = script_path

        # def execute_script(ApplicationWindow):
        #
        #     script_name = str(ApplicationWindow.cmb_execute.currentText())
        #
        #     if script_name == 'ESR':
        #
        #         ApplicationWindow.statusBar().showMessage('starting esr script',1000)
        #         load_parameter
        #
        #         DeviceTriggers.runESR(float(ApplicationWindow.rfPower.text),float(ApplicationWindow.freqMin.text),float(ApplicationWindow.freqMax.text),float(ApplicationWindow.numPtsESR.text), ApplicationWindow.esrQueue)
        #
        #
        #         ApplicationWindow.path_script.setText(ApplicationWindow.parameters_paths_scripts[])

        def execute_script(ApplicationWindow):
            script_name = str(ApplicationWindow.cmb_execute.currentText())
            script_path = ApplicationWindow.parameters_paths_scripts[script_name]
            ApplicationWindow.statusBar().showMessage('running {:s} with {:s}'.format(script_name, script_path),1000)
            ApplicationWindow.path_script.setText(script_path)

            if script_name == 'ESR (grid)':
                _, pt_a, pt_b, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                points = Meshing.get_points_on_a_grid(pt_a, pt_b, xpts, ypts)
                esr_param = ESR.ESR_load_param(ApplicationWindow.path_script.text())
                print 'ESR (grid)'
                ESR.ESR_map(points, esr_param)

            elif script_name == 'AutoFocus':
                print 'need to implement AutoFocus'
                _, pt_a, pt_b, _, _, _ = get_pts_and_size(ApplicationWindow)
                roi_focus = Meshing.two_pts_to_roi(pt_a, pt_b)
                af_parameter = AF.AF_load_param(ApplicationWindow.path_script.text())
                voltage_focus = AF.autofocus_RoI(af_parameter, roi_focus)

                ApplicationWindow.statusBar().showMessage('new focus {:0.3f}'.format(voltage_focus),2000)

    ##################################################################################
    # ADD GLOBAL ####################################################################
    ##################################################################################
    def add_global():




        row_start = 1
        column_start =  1

        ApplicationWindow.button_load_settings = QtGui.QPushButton('load settings', ApplicationWindow.main_widget)
        ApplicationWindow.button_load_settings.clicked.connect(lambda: load_settings(ApplicationWindow))
        ApplicationWindow.grid_global.addWidget(ApplicationWindow.button_load_settings,row_start,column_start)

        ApplicationWindow.button_save_settings = QtGui.QPushButton('save settings', ApplicationWindow.main_widget)
        ApplicationWindow.button_save_settings.clicked.connect(lambda: save_settings(ApplicationWindow))
        ApplicationWindow.grid_global.addWidget(ApplicationWindow.button_save_settings,row_start,column_start+1)

        ApplicationWindow.button_exit = QtGui.QPushButton('exit', ApplicationWindow.main_widget)
        ApplicationWindow.grid_global.addWidget(ApplicationWindow.button_exit,row_start,column_start+2)

        # settings
        ApplicationWindow.cmb_APD = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_APD.addItems(['Use APD', 'Use Diode'])
        # ApplicationWindow.cmb_APD.changeEvent(ApplicationWindow.button_APD)
        # ApplicationWindow.button_APD = QtGui.QPushButton('Use APD',ApplicationWindow.main_widget)
        # ApplicationWindow.button_APD.setCheckable(True)
        # ApplicationWindow.button_APD.setChecked(True)
        # ApplicationWindow.button_APD.clicked.connect(ApplicationWindow.button_APD)
        ApplicationWindow.grid_global.addWidget(ApplicationWindow.cmb_APD,1,16)

    ##################################################################################
    # ADD SETTINGS ####################################################################
    ##################################################################################
    def add_settings():


        click_id = None

        def get_image_point(pt_id):

            def clicked_image(eclick):

                x = '{:0.4f}'.format(eclick.xdata)
                y = '{:0.4f}'.format(eclick.ydata)
                if pt_id == 'a':
                    ApplicationWindow.txt_pt_2a_x.setText(x)
                    ApplicationWindow.txt_pt_2a_y.setText(y)
                elif pt_id == 'b':
                    ApplicationWindow.txt_pt_2b_x.setText(x)
                    ApplicationWindow.txt_pt_2b_y.setText(y)



                ApplicationWindow.imPlot.mpl_disconnect(click_id)
                display_shapes()


            click_id = ApplicationWindow.imPlot.mpl_connect('button_press_event', clicked_image)





        row_start = 1
        column_start =  1

        ApplicationWindow.label_scan_1a = QtGui.QLabel("pt 1a (scan)", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_scan_1a,row_start,column_start)
        ApplicationWindow.label_scan_1b = QtGui.QLabel("pt 1b (scan)", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_scan_1b,row_start+1,column_start)
        ApplicationWindow.label_pts_1 = QtGui.QLabel("# pts 1", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_pts_1,row_start+2,column_start)
        ApplicationWindow.button_scan_2a = QtGui.QPushButton('pt 2a', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan_2a.clicked.connect(lambda: get_image_point('a'))
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.button_scan_2a,row_start+3,column_start)
        ApplicationWindow.button_scan_2b = QtGui.QPushButton('pt 2b', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan_2b.clicked.connect(lambda: get_image_point('b'))
        # ApplicationWindow.button_scan_2b.clicked.connect(lambda: ApplicationWindow.imPlot.mpl_connect('button_press_event', lambda x: get_image_point(x, 'b')))
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.button_scan_2b,row_start+4,column_start)
        ApplicationWindow.label_pts_2 = QtGui.QLabel("# pts 2", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_pts_2,row_start+5,column_start)
        ApplicationWindow.label_laser = QtGui.QLabel("laser", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_laser,row_start+6,column_start)

        ApplicationWindow.label_x = QtGui.QLabel("x", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_x,row_start-1,column_start+1)
        ApplicationWindow.txt_pt_1a_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1a_x,row_start,column_start+1)
        ApplicationWindow.txt_pt_1b_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1b_x,row_start+1,column_start+1)
        ApplicationWindow.txt_pt_1_x_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1_x_pts,row_start+2,column_start+1)
        ApplicationWindow.txt_pt_2a_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2a_x,row_start+3,column_start+1)
        ApplicationWindow.txt_pt_2b_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2b_x,row_start+4,column_start+1)
        ApplicationWindow.txt_pt_2_x_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2_x_pts,row_start+5,column_start+1)
        ApplicationWindow.txt_pt_laser_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_laser_x,row_start+6,column_start+1)

        ApplicationWindow.label_y = QtGui.QLabel("y", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_y,row_start-1,column_start+2)
        ApplicationWindow.txt_pt_1a_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1a_y,row_start,column_start+2)
        ApplicationWindow.txt_pt_1b_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1b_y,row_start+1,column_start+2)
        ApplicationWindow.txt_pt_1_y_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_1_y_pts,row_start+2,column_start+2)
        ApplicationWindow.txt_pt_2a_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2a_y,row_start+3,column_start+2)
        ApplicationWindow.txt_pt_2b_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2b_y,row_start+4,column_start+2)
        ApplicationWindow.txt_pt_2_y_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_2_y_pts,row_start+5,column_start+2)
        ApplicationWindow.txt_pt_laser_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_pt_laser_y,row_start+6,column_start+2)

        ApplicationWindow.button_set_laser = QtGui.QPushButton('set laser', ApplicationWindow.main_widget)
        ApplicationWindow.button_set_laser.clicked.connect(lambda : set_laser(None))
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.button_set_laser,row_start+3,column_start+3)


        ApplicationWindow.label_time_per_pt = QtGui.QLabel("time per pt", ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.label_time_per_pt,row_start,column_start+3)
        ApplicationWindow.txt_time_per_pt = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_settings.addWidget(ApplicationWindow.txt_time_per_pt,row_start+1,column_start+3)

# ApplicationWindow.RS = RectangleSelector(ApplicationWindow.imPlot.axes, ApplicationWindow.select_RoI, button = 3, drawtype='box', rectprops = rectprops)


    ##################################################################################
    # ADD DISPLAY ####################################################################
    ##################################################################################
    def add_display():

        def execute_scan():

            remove_patches()

            ApplicationWindow.statusBar().showMessage("Taking Image",0)

            if ApplicationWindow.zoomed_in:
                ApplicationWindow.txt_pt_1a_x.setText(ApplicationWindow.txt_pt_2a_x.text())
                ApplicationWindow.txt_pt_1b_x.setText(ApplicationWindow.txt_pt_2b_x.text())
                ApplicationWindow.txt_pt_1a_y.setText(ApplicationWindow.txt_pt_2a_y.text())
                ApplicationWindow.txt_pt_1b_y.setText(ApplicationWindow.txt_pt_2b_y.text())

            ApplicationWindow.zoomed_in = False

            pta_x = float(ApplicationWindow.txt_pt_1a_x.text())
            ptb_x = float(ApplicationWindow.txt_pt_1b_x.text())
            pta_y = float(ApplicationWindow.txt_pt_1a_y.text())
            ptb_y = float(ApplicationWindow.txt_pt_1b_y.text())

            xMin = min([pta_x, ptb_x])
            xMax = max([pta_x, ptb_x])
            yMin = min([pta_y, ptb_y])
            yMax = max([pta_y, ptb_y])

            pts_x = float(ApplicationWindow.txt_pt_1_x_pts.text())
            pts_y = float(ApplicationWindow.txt_pt_1_y_pts.text())

            timePerPt = float(ApplicationWindow.txt_time_per_pt.text())

            bool_use_apd = str(ApplicationWindow.cmb_APD.currentText()) == 'Use APD'
            ApplicationWindow.imageData, ApplicationWindow.imageRoI = DeviceTriggers.scanGui(ApplicationWindow.imPlot,xMin,xMax,pts_x,yMin,yMax,pts_y,timePerPt, ApplicationWindow.scan_queue, bool_use_apd)

            set_laser([xMax, yMax])

            ApplicationWindow.statusBar().clearMessage()
            display_shapes()
            # if(ApplicationWindow.autosaveCheck.isChecked() == True):
            #     ApplicationWindow.saveImageClicked()

        def zoom_RoI_in():
            _, pt_a, pt_b, _, _, _ = get_pts_and_size(ApplicationWindow)
            xmin  = min(pt_a[0],pt_b[0])
            xmax  = max(pt_a[0],pt_b[0])
            ymin  = min(pt_a[1],pt_b[1])
            ymax  = max(pt_a[1],pt_b[1])

            ApplicationWindow.imPlot.axes.set_xlim(left= xmin, right =xmax)
            ApplicationWindow.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
            ApplicationWindow.imPlot.draw()

            ApplicationWindow.zoomed_in = True

        def zoom_RoI_out():
            pt_a = [float(ApplicationWindow.txt_pt_1a_x.text()), float(ApplicationWindow.txt_pt_1a_y.text())]
            pt_b = [float(ApplicationWindow.txt_pt_1b_x.text()), float(ApplicationWindow.txt_pt_1b_y.text())]

            xmin  = min(pt_a[0],pt_b[0])
            xmax  = max(pt_a[0],pt_b[0])
            ymin  = min(pt_a[1],pt_b[1])
            ymax  = max(pt_a[1],pt_b[1])

            ApplicationWindow.imPlot.axes.set_xlim(left= xmin, right =xmax)
            ApplicationWindow.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
            ApplicationWindow.imPlot.draw()

            ApplicationWindow.zoomed_in = False

        def interrupt_scan():
            ApplicationWindow.scan_queue.put('STOP')




        ApplicationWindow.patches = []

        row_start = 1
        column_start =  1

        ApplicationWindow.radio_roi = QtGui.QCheckBox("&region of interest (RoI)")
        ApplicationWindow.radio_roi.clicked.connect(display_shapes)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.radio_roi,row_start, column_start)
        ApplicationWindow.radio_grid = QtGui.QCheckBox("Grid")
        ApplicationWindow.radio_grid.clicked.connect(display_shapes)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.radio_grid,row_start +1, column_start)
        ApplicationWindow.radio_line = QtGui.QCheckBox("Line")
        ApplicationWindow.radio_line.clicked.connect(display_shapes)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.radio_line,row_start +2, column_start)
        ApplicationWindow.radio_pt2 = QtGui.QCheckBox("pt 2a")
        ApplicationWindow.radio_pt2.clicked.connect(display_shapes)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.radio_pt2,row_start +3, column_start)
        ApplicationWindow.radio_laser = QtGui.QCheckBox("Laser")
        ApplicationWindow.radio_laser.clicked.connect(display_shapes)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.radio_laser,row_start +4, column_start)

        # set RoI and zoom
        ApplicationWindow.button_zoom_in_RoI = QtGui.QPushButton('zoom in (RoI)',ApplicationWindow.main_widget)
        ApplicationWindow.button_zoom_in_RoI.clicked.connect(zoom_RoI_in)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_zoom_in_RoI,row_start,column_start+1)
        ApplicationWindow.button_zoom_out_RoI = QtGui.QPushButton('zoom out', ApplicationWindow.main_widget)
        ApplicationWindow.button_zoom_out_RoI.clicked.connect(zoom_RoI_out)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_zoom_out_RoI,row_start,column_start+2)

        # colar bar
        ApplicationWindow.cbar_max = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.cbar_max,row_start +5, column_start)
        ApplicationWindow.label_cbar_max = QtGui.QLabel("Colorbar Threshold", ApplicationWindow.main_widget)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.label_cbar_max,row_start +5, column_start +1)
        ApplicationWindow.button_cbar_thresh = QtGui.QPushButton('Update Colorbar', ApplicationWindow.main_widget)
        ApplicationWindow.button_cbar_thresh.clicked.connect(ApplicationWindow.cbarThreshClicked)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_cbar_thresh,row_start +5, column_start +2)

        ApplicationWindow.button_stop = QtGui.QPushButton('Stop Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_stop.clicked.connect(interrupt_scan)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_stop,row_start +6,column_start)
        ApplicationWindow.button_scan = QtGui.QPushButton('Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan.clicked.connect(execute_scan)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_scan,row_start +6,column_start+1)

        ApplicationWindow.button_stop = QtGui.QPushButton('Stop Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_stop.clicked.connect(interrupt_scan)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_stop,row_start +6,column_start)
        ApplicationWindow.button_scan = QtGui.QPushButton('Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan.clicked.connect(execute_scan)
        ApplicationWindow.grid_display.addWidget(ApplicationWindow.button_scan,row_start +6,column_start+1)

        ApplicationWindow.scan_queue = Queue.Queue()






    # def zoom_RoI(ApplicationWindow):
    #     ApplicationWindow.setRoI(ApplicationWindow.RoI)
    #
    #     xmin, xmax, ymin, ymax = roi_to_min_max(ApplicationWindow.RoI)
    #     ApplicationWindow.imPlot.axes.set_xlim(left= xmin, right =xmax)
    #     ApplicationWindow.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
    #     if(not ApplicationWindow.circ==None):
    #         ApplicationWindow.drawDot()
    #     ApplicationWindow.imPlot.draw()



    ##################################################################################
    ##### GRID IMAGE #################################################################
    ##################################################################################
    # ApplicationWindow.grid_image = QtGui.QGridLayout()
    # vbox_main.addLayout(ApplicationWindow.grid_image)

    ApplicationWindow.imPlot = gui_cw.MyMplCanvas(ApplicationWindow.main_widget, width=5, height=4, dpi=100)
    plotBox.addWidget(ApplicationWindow.imPlot)

    #ApplicationWindow.imageData = None
    ApplicationWindow.imageData = np.array(pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-27_18-41-56-NVBaselineTests.csv"))
    ApplicationWindow.imPlot.axes.imshow(ApplicationWindow.imageData, extent = [-.05,.05,-.05,.05])
    ApplicationWindow.imPlot.draw()

    # ApplicationWindow.mouseNVImageConnect = ApplicationWindow.imPlot.mpl_connect('button_press_event', ApplicationWindow.mouseNVImage)
    # rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
    # ApplicationWindow.RS = RectangleSelector(ApplicationWindow.imPlot.axes, ApplicationWindow.select_RoI, button = 3, drawtype='box', rectprops = rectprops)

    ##### GRID CONTROLS ############################################################################################
    ################################################################################################################

    ApplicationWindow.grid_controls = QtGui.QGridLayout()
    vbox_main.addLayout(ApplicationWindow.grid_controls)



    ##### settings #################################################################################################


    ApplicationWindow.group_settings = QtGui.QGroupBox("Settings")
    ApplicationWindow.grid_settings = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_settings,1,1)
    ApplicationWindow.group_settings.setLayout(ApplicationWindow.grid_settings)

    add_settings()



    ##### display #################################################################################################
    ApplicationWindow.group_display = QtGui.QGroupBox("Display")
    # ApplicationWindow.group_display.isCheckable()
    ApplicationWindow.grid_display = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_display,1,2)
    ApplicationWindow.group_display.setLayout(ApplicationWindow.grid_display)

    add_display()



    ##### execute #################################################################################################
    ApplicationWindow.group_execute = QtGui.QGroupBox("Execute")
    ApplicationWindow.grid_execute = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_execute,2,1)
    ApplicationWindow.group_execute.setLayout(ApplicationWindow.grid_execute)

    add_execute()


    ##### global #################################################################################################
    ApplicationWindow.group_global = QtGui.QGroupBox("global")
    ApplicationWindow.grid_global = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_global,2,2)
    ApplicationWindow.group_global.setLayout(ApplicationWindow.grid_global)

    add_global()


    ApplicationWindow.zoomed_in = False
    load_settings(ApplicationWindow, 'Z://Lab//Cantilever//Measurements//default.set')

    display_shapes()
    QtGui.QApplication.processEvents()


def load_settings(ApplicationWindow, filename = None):

    def dict_to_values_settings(ApplicationWindow, dict):
        ApplicationWindow.txt_pt_1a_x.setText(dict['pt_1a_x'])
        ApplicationWindow.txt_pt_1b_x.setText(dict['pt_1b_x'])
        ApplicationWindow.txt_pt_2a_x.setText(dict['pt_2a_x'])
        ApplicationWindow.txt_pt_2b_x.setText(dict['pt_2b_x'])
        ApplicationWindow.txt_pt_1a_y.setText(dict['pt_1a_y'])
        ApplicationWindow.txt_pt_1b_y.setText(dict['pt_1b_y'])
        ApplicationWindow.txt_pt_2a_y.setText(dict['pt_2a_y'])
        ApplicationWindow.txt_pt_2b_y.setText(dict['pt_2b_y'])
        ApplicationWindow.txt_pt_1_x_pts.setText(dict['pt_1_x'])
        ApplicationWindow.txt_pt_1_y_pts.setText(dict['pt_1_y'])
        ApplicationWindow.txt_pt_2_x_pts.setText(dict['pt_2_x'])
        ApplicationWindow.txt_pt_2_y_pts.setText(dict['pt_2_y'])
        ApplicationWindow.txt_pt_laser_x.setText(dict['pt_laser_x'])
        ApplicationWindow.txt_pt_laser_y.setText(dict['pt_laser_y'])
        ApplicationWindow.txt_time_per_pt.setText(dict['txt_time_per_pt'])
    def dict_to_values_display(ApplicationWindow, dict):
        ApplicationWindow.radio_roi.setChecked(dict['show_roi'] == "True" )
        ApplicationWindow.radio_line.setChecked(dict['show_line'] == "True")
        ApplicationWindow.radio_grid.setChecked(dict['show_grid'] == "True")
        ApplicationWindow.radio_laser.setChecked(dict['show_laser'] == "True")


    def dict_to_values_execute(ApplicationWindow, dict):

        # print ApplicationWindow.parameters_paths_scripts
        ApplicationWindow.parameters_paths_scripts = dict['parameters_paths_script']
        # print '1', ApplicationWindow.parameters_paths_scripts
        ApplicationWindow.cmb_execute.setCurrentIndex(ApplicationWindow.cmb_execute.findText(dict['selected_script']))
        ApplicationWindow.path_script.setText(dict['parameters_paths_script'][dict['selected_script']])





    def dict_to_values_global(ApplicationWindow, dict):

        ApplicationWindow.cmb_APD.setCurrentIndex(ApplicationWindow.cmb_APD.findText(dict['selected_detector']))


    if filename is None:
        filename = QtGui.QFileDialog.getOpenFileName(ApplicationWindow, 'Open file', 'Z://Lab//Cantilever//Measurements//', '*.set')

    if not filename == '':
        settings = rw.load_json(filename)

        # print settings
        dict_to_values_settings(ApplicationWindow, settings['settings'])
        dict_to_values_display(ApplicationWindow, settings['display'])
        dict_to_values_execute(ApplicationWindow, settings['execute'])
        dict_to_values_global(ApplicationWindow, settings['global'])


        ApplicationWindow.statusBar().showMessage('loaded {:s}'.format(filename),0)


def save_settings(ApplicationWindow, set_filename = None):
    '''
     saves the setting
    '''
    def values_to_dict_settings(ApplicationWindow):

        dict = {
            "pt_1a_x": str(ApplicationWindow.txt_pt_1a_x.text()),
            "pt_1b_x": str(ApplicationWindow.txt_pt_1b_x.text()),
            "pt_2a_x": str(ApplicationWindow.txt_pt_2a_x.text()),
            "pt_2b_x": str(ApplicationWindow.txt_pt_2b_x.text()),
            "pt_1a_y": str(ApplicationWindow.txt_pt_1a_y.text()),
            "pt_1b_y": str(ApplicationWindow.txt_pt_1b_y.text()),
            "pt_2a_y": str(ApplicationWindow.txt_pt_2a_y.text()),
            "pt_2b_y": str(ApplicationWindow.txt_pt_2b_y.text()),
            "pt_1_x": str(ApplicationWindow.txt_pt_1_x_pts.text()),
            "pt_1_y": str(ApplicationWindow.txt_pt_1_y_pts.text()),
            "pt_2_x": str(ApplicationWindow.txt_pt_2_x_pts.text()),
            "pt_2_y": str(ApplicationWindow.txt_pt_2_y_pts.text()),
            "pt_laser_x": str(ApplicationWindow.txt_pt_laser_x.text()),
            "pt_laser_y": str(ApplicationWindow.txt_pt_laser_y.text()),
            "txt_time_per_pt": str(ApplicationWindow.txt_time_per_pt.text())
        }
        return dict
    def values_to_dict_display(ApplicationWindow):

        dict = {
            "show_roi": str(ApplicationWindow.radio_roi.isChecked()),
            "show_line": str(ApplicationWindow.radio_line.isChecked()),
            "show_grid": str(ApplicationWindow.radio_grid.isChecked()),
            "show_laser": str(ApplicationWindow.radio_laser.isChecked())
        }
        return dict
    def values_to_dict_execute(ApplicationWindow):

        dict = {
            "selected_script": str(ApplicationWindow.cmb_execute.currentText()),
            # 'path_script': str(ApplicationWindow.path_script.text()),
            'parameters_paths_script':  ApplicationWindow.parameters_paths_scripts
        }

        return dict
    def values_to_dict_global(ApplicationWindow):

        dict = {
            "selected_detector": str(ApplicationWindow.cmb_APD.currentText())
        }
        return dict

    if set_filename is None:
        set_filename = QtGui.QFileDialog.getSaveFileName(ApplicationWindow, 'select file', 'Z://Lab//Cantilever//Measurements//', '*.set')


    if not set_filename == '':
        dict_settings = values_to_dict_settings(ApplicationWindow)
        dict_display = values_to_dict_display(ApplicationWindow)
        dict_execute = values_to_dict_execute(ApplicationWindow)
        dict_global = values_to_dict_global(ApplicationWindow)

        dict_all = {
            'settings':dict_settings,
            'display':dict_display,
            'execute':dict_execute,
            'global':dict_global
        }

        rw.save_json(dict_all, set_filename)
        # with open(set_filename, 'w') as outfile:
        #     tmp = json.dump(dict_all, outfile, indent=4)

        ApplicationWindow.statusBar().showMessage('saved {:s}'.format(set_filename),0)

def get_pts_and_size(ApplicationWindow):
    pt_a = [float(ApplicationWindow.txt_pt_2a_x.text()), float(ApplicationWindow.txt_pt_2a_y.text())]
    pt_b = [float(ApplicationWindow.txt_pt_2b_x.text()), float(ApplicationWindow.txt_pt_2b_y.text())]
    pt_L = [float(ApplicationWindow.txt_pt_laser_x.text()), float(ApplicationWindow.txt_pt_laser_y.text())]
    xrange = ApplicationWindow.imPlot.axes.get_xlim()[1]-ApplicationWindow.imPlot.axes.get_xlim()[0]
    yrange = ApplicationWindow.imPlot.axes.get_ylim()[1]-ApplicationWindow.imPlot.axes.get_ylim()[0]
    size= .01*min(xrange,yrange)

    xpts = float(ApplicationWindow.txt_pt_2_x_pts.text())
    ypts = float(ApplicationWindow.txt_pt_2_y_pts.text())
    return size, pt_a, pt_b, xpts, ypts, pt_L


def exec_scriptBtnClicked(ApplicationWindow):
    '''
        run script to repeatedly take images and set laser pointer to predefined location
    '''


    dirpath = ApplicationWindow.saveLocImage.text()
    tag = ApplicationWindow.saveTagImage.text()
    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    filepath_set = dirpath + "\\" + start_time + '_' + tag + '.set'

    ApplicationWindow.save_settings(filepath_set)


    nr_meas = 20
    i = 0
    while i < nr_meas:
        ApplicationWindow.scanBtnClicked()
        ApplicationWindow.vSetBtnClicked()
        ApplicationWindow.saveImageClicked()


        waittime = 60 # 1 min
        while waittime > 0:
            waittime -= 1
            time.sleep(1)
            ApplicationWindow.statusBar().showMessage('scan {:d}/{:d}: time until next scan: {:d}s'.format(i, nr_meas, waittime),1000)
            QtGui.QApplication.processEvents()

        i += 1

