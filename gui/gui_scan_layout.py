__author__ = 'Experiment'

import json as json
import Queue
import time

from PyQt4 import QtGui
import numpy as np
import pandas as pd
import scipy.spatial
import matplotlib.patches as patches
import Image
import atexit

import gui_custom_widgets as gui_cw
import helper_functions.reading_writing as rw
from gui import GuiDeviceTriggers as DeviceTriggers
import helper_functions.meshing as Meshing
import scripts.ESR_many_NVs as ESR
import scripts.auto_focus as AF
from functions import track_NVs as track
from scripts import set_focus as f
from hardware_modules import PiezoController as PC
from scripts import ZiControl_many_pts as ZIControl
from gui import PlotAPDCounts2 as Cnts

# This function should be called from the PYQT main loop. It implements all of the widgets in the gui
def add_scan_layout(ApplicationWindow, vbox_main, plotBox):

    def display_shapes():
        '''
        Displays patches for roi, laser, grid, etc on image
        '''
        # ApplicationWindow.imPlot.axes.imshow(ApplicationWindow.imageData, extent = [-.05,.05,-.05,.05])
        # checks which patches are toggled on
        if ApplicationWindow.radio_roi.isChecked()==True:
            get_roi_patch(ApplicationWindow)
        if ApplicationWindow.radio_grid.isChecked()==True:
            get_grid_patches(ApplicationWindow)
        if ApplicationWindow.radio_line.isChecked()==True:
            get_line_patches(ApplicationWindow)
        if ApplicationWindow.radio_laser.isChecked()==True:
            get_dot_patch_laser(ApplicationWindow)
        if ApplicationWindow.radio_pt2.isChecked()==True:
            get_dot_patch_pt2(ApplicationWindow)
        if ApplicationWindow.plot_nvs == True:
            get_dot_patches_nv_points(ApplicationWindow)
        if ApplicationWindow.radio_NVs.isChecked()==True:
            get_dot_patches_selected_points(ApplicationWindow)

        if(not ApplicationWindow.patches==[]):
            # ApplicationWindow.imPlot.axes.add_collection(ApplicationWindow.patches)
            for patch in ApplicationWindow.patches:
                ApplicationWindow.imPlot.axes.add_patch(patch)

        if ApplicationWindow.radio_NV_labels.isChecked()==True:
            display_point_labels(ApplicationWindow)

        ApplicationWindow.imPlot.draw()


    def reset_shapes():
        '''
        Removes current patches and regenerates them, to be called when anything changing what patches are needed
        '''

        remove_patches(ApplicationWindow)
        display_shapes()



    def display_point_labels(ApplicationWindow):
        '''
        Goes through list of chosen NVs and display number, corresponding to order ini which they will be processed
        :param ApplicationWindow:
        '''
        nv_num = 1
        for nv_pt in ApplicationWindow.selected_points:
            ApplicationWindow.imPlot.axes.text(nv_pt[0], nv_pt[1], ' ' + str(nv_num), color = 'k')
            nv_num += 1

    def get_dot_patch_pt2(ApplicationWindow):
        '''
        place yellow dot at pt_a and appends to patchlist
        :param ApplicationWindow:
        '''
        size, pt_a, _, _,_,_,_ = get_pts_and_size(ApplicationWindow)
        ApplicationWindow.patches.append(patches.Circle((pt_a[0], pt_a[1]), 2*size, fc = 'y'))

    def get_dot_patches_nv_points(ApplicationWindow):
        '''
        adds the previously selected points as patches to the image
        '''

        size,_,_,_,_,_,_ = get_pts_and_size(ApplicationWindow)
        if not ApplicationWindow.nv_points == []:
            for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'r') for pt in ApplicationWindow.nv_points]:
                ApplicationWindow.patches.append(patch)

    def get_dot_patches_selected_points(ApplicationWindow):
        '''
        adds the previously selected points as patches to the image
        '''

        size,_,_,_,_,_,_ = get_pts_and_size(ApplicationWindow)
        if not ApplicationWindow.selected_points == []:
            for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'b') for pt in ApplicationWindow.selected_points]:
                ApplicationWindow.patches.append(patch)


    def get_dot_patch_laser(ApplicationWindow):
        '''
        place yellow dot at pt_L, the location of the laser, and appends to patchlist
        :param ApplicationWindow:
        '''
        size, _, _,_,_,_,pt_L = get_pts_and_size(ApplicationWindow)
        ApplicationWindow.patches.append(patches.Circle((pt_L[0], pt_L[1]), 3*size, fc = 'r'))

    def get_line_patches(ApplicationWindow):
        '''
        generates xpts number of points between pt_a and pt_b
        :param ApplicationWindow:
        '''
        size, pt_a, pt_b, _, xpts, _,_  = get_pts_and_size(ApplicationWindow)
        points = Meshing.get_points_along_line(pt_a, pt_b, xpts)

        for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'g') for pt in points]:
            ApplicationWindow.patches.append(patch)

    def get_grid_patches(ApplicationWindow):
        '''
        generates an xpts x ypts grid of white circles, using pt_a and pt_b as the corners for a straight grid, or
                pt_a and pt_b to define a line and pt_c to define a distance from that line for an angled grid
        :param ApplicationWindow:
        '''
        size, pt_a, pt_b, pt_c, xpts, ypts,_  = get_pts_and_size(ApplicationWindow)
        # checks if grid should be straight vertical/horizontal or angled
        if ApplicationWindow.radio_angled_grid.isChecked():
            points = Meshing.get_points_on_a_grid_angled(pt_a, pt_b, pt_c, xpts, ypts)
        else:
            points = Meshing.get_points_on_a_grid(pt_a, pt_b, xpts, ypts)

        for patch in [patches.Circle((pt[0], pt[1]), size, fc = 'w') for pt in points]:
            ApplicationWindow.patches.append(patch)

    def get_roi_patch(ApplicationWindow):
        size, pt_a, pt_b ,_,_,_,_ = get_pts_and_size(ApplicationWindow)

        center, w, h = Meshing.two_pts_to_center_size(pt_a, pt_b)

        ApplicationWindow.patches.append(patches.Rectangle((center[0] - w /2., center[1] - h/2.),
                           width = w, height = h , fc = 'none' , ec = 'r'))

        
    def choosing_points(ApplicationWindow):

        if(ApplicationWindow.button_select_NVs.isChecked()):
            def select_point(event, coordinates):
                if(not(event.xdata == None)):
                    if(event.button == 1):
                        pt = np.array([event.xdata,event.ydata])
                        tree = scipy.spatial.KDTree(coordinates)
                        _,i = tree.query(pt)
                        nv_pt = coordinates[i].tolist()
                        if (nv_pt in ApplicationWindow.selected_points):
                            ApplicationWindow.selected_points.remove(nv_pt)
                            for circ in ApplicationWindow.esr_select_patches:
                                if (nv_pt == np.array(circ.center)).all():
                                    ApplicationWindow.esr_select_patches.remove(circ)
                                    circ.remove()
                                    break
                        else:
                            ApplicationWindow.selected_points.append(nv_pt)
                            size, _,_,_,_,_, _ = get_pts_and_size(ApplicationWindow,'1')
                            circ = patches.Circle((nv_pt[0], nv_pt[1]), size, fc = 'b')
                            ApplicationWindow.imPlot.axes.add_patch(circ)
                            ApplicationWindow.esr_select_patches.append(circ)
                        ApplicationWindow.imPlot.draw()

            def find_pts(voltage_range, numPts):
                if ApplicationWindow.is_choosing_points == True:
                    ApplicationWindow.imPlot.mpl_disconnect(ApplicationWindow.select_point)
                ApplicationWindow.plot_nvs = True
                ApplicationWindow.is_choosing_points = True
                ApplicationWindow.statusBar().showMessage("Choose NVs for ESR", 0)
                coordinates = track.locate_NVs(ApplicationWindow.imageData, voltage_range, numPts)
                coordinates[:,[0,1]] = coordinates[:,[1,0]]
                _, pt1, pt2, _, xPts, yPts, _ = get_pts_and_size(ApplicationWindow,'1')
                nv_roi = Meshing.two_pts_to_roi(pt1, pt2, xPts, yPts)
                coordinates_in_volt = track.pixel_to_voltage(coordinates, ApplicationWindow.imageData, nv_roi)
                ApplicationWindow.nv_points = coordinates_in_volt
                display_shapes()
                ApplicationWindow.esr_select_patches = []

            def choose_subset():
                point_selected = ApplicationWindow.imPlot.mpl_connect('button_press_event', lambda x: select_point(x, ApplicationWindow.nv_points))
                ApplicationWindow.selected_points = list()
                ApplicationWindow.is_choosing_points = True
                while ApplicationWindow.is_choosing_points:
                    QtGui.QApplication.processEvents()
                    time.sleep(.05)
                ApplicationWindow.imPlot.mpl_disconnect(select_point)
                QtGui.QApplication.processEvents()
                dirpath = ApplicationWindow.txt_save_image_location.text()
                start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                filepath = dirpath + "\\" + start_time
                filepathJPG = filepath + '.jpg'
                ApplicationWindow.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')
                ApplicationWindow.plot_nvs = False
                for circ in ApplicationWindow.esr_select_patches:
                    circ.remove()
                reset_shapes()

            voltage_range = abs(float(ApplicationWindow.txt_pt_1a_x.text()) - float(ApplicationWindow.txt_pt_1b_x.text()))
            numPts = float(ApplicationWindow.txt_pt_1_x_pts.text())

            find_pts(voltage_range, numPts)
            choose_subset()



        else:
            ApplicationWindow.is_choosing_points = False


        # df = pd.DataFrame(ApplicationWindow.esr_NVs)
        # dfimg = pd.DataFrame(ApplicationWindow.imageData)
        # dirpath = ApplicationWindow.esrSaveLoc.text()
        # start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        # filepath = dirpath + "\\" + start_time
        # filepathCSV = filepath + '.csv'
        # filepathImg = filepath + 'baselineimg.csv'
        # filepathJPG = filepath + '.jpg'
        # filepathRoI = filepath + '.roi'
        # df.to_csv(filepathCSV, index = False, header=False)
        # dfimg.to_csv(filepathImg, index = False, header=False)
        # ApplicationWindow.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')
        # ApplicationWindow.saveRoI(ApplicationWindow.RoI, filepathRoI)
        # ApplicationWindow.esrReadLoc.setText(filepath)
        # ApplicationWindow.statusBar().clearMessage()
        # ApplicationWindow.esr_running = False



    #def end_choosing_points(ApplicationWindow):
    #    ApplicationWindow.is_choosing_points = False
    #    print(ApplicationWindow.esr_NVs)
        
        
        
        
    def remove_patches(ApplicationWindow):
        if(not ApplicationWindow.patches==[]):
            print ApplicationWindow.patches
            for patch in ApplicationWindow.patches:
                # patch.remove() randomly fails for unknown reason. This skips that failed patch. No adverse issues
                # seem to occur
                try:
                    patch.remove()
                except NotImplementedError:
                    continue
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

        reset_shapes()

        ApplicationWindow.statusBar().showMessage("Galvo Position Updated",2000)

    def copy_scan_params():
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText("xVmin = " + ApplicationWindow.txt_pt_2a_x.text() + "\nyVmin = " + ApplicationWindow.txt_pt_2a_y.text() + "\nxVmax = " + ApplicationWindow.txt_pt_2b_x.text() + "\nyVmax = " + ApplicationWindow.txt_pt_2b_y.text() + "\nxPts = " + ApplicationWindow.txt_pt_1_x_pts.text() + "\nyPts = " + ApplicationWindow.txt_pt_1_y_pts.text() + "\ntimerPerPt = " + ApplicationWindow.txt_time_per_pt.text(), mode=cb.Clipboard)

    ##################################################################################
    # ADD EXECUTE ####################################################################
    ##################################################################################






    def add_execute(grid, row_start = 1, column_start =  1):

        ApplicationWindow.label_execute = QtGui.QLabel('execute', ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_execute,row_start,column_start)
        ApplicationWindow.cmb_execute = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_execute.addItems(['ESR (chosen NVs)', 'ESR (grid)', 'ESR (point)', 'AutoFocus', 'AutoFocus (mean)', 'AutoFocus (mean, grid)', 'Counter', 'Get Distance', 'ZI Frequency Sweep (point)', 'ZI Frequency Sweep (grid)', 'reset scan range'])
        ApplicationWindow.cmb_execute.activated.connect(lambda: change_script(ApplicationWindow))
        grid.addWidget(ApplicationWindow.cmb_execute,row_start+1,column_start)

        ApplicationWindow.label_settings = QtGui.QLabel('script settings', ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_settings,row_start,column_start+1)
        ApplicationWindow.path_script = QtGui.QLineEdit(ApplicationWindow.main_widget)
        ApplicationWindow.path_script.textChanged.connect(lambda: change_script_path(ApplicationWindow))
        # ApplicationWindow.path_script.setText('Z:\\Lab\\Cantilever\\Measurements')
        grid.addWidget(ApplicationWindow.path_script,row_start+1,column_start+1)

        ApplicationWindow.button_execute_script = QtGui.QPushButton('run script', ApplicationWindow.main_widget)
        ApplicationWindow.button_execute_script.clicked.connect(lambda: execute_script(ApplicationWindow))
        grid.addWidget(ApplicationWindow.button_execute_script,row_start+1,column_start+2)

        ApplicationWindow.button_stop_script = QtGui.QPushButton('stop script', ApplicationWindow.main_widget)
        ApplicationWindow.button_stop_script.clicked.connect(lambda: stop_script(ApplicationWindow))
        grid.addWidget(ApplicationWindow.button_stop_script,row_start+1,column_start+3)

        ApplicationWindow.selected_points = list()


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
            ApplicationWindow.script_queue = Queue.Queue()

            print ApplicationWindow.path_script.text()

            if script_name == 'ESR (chosen NVs)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                esr_param = ESR.ESR_load_param(ApplicationWindow.path_script.text())
                roi_focus = Meshing.two_pts_to_roi(pt_a2, pt_b2)
                print 'ESR (chosen NVs)'
                if not ApplicationWindow.selected_points:
                    QtGui.QMessageBox.information(ApplicationWindow.main_widget, "No NVs Error","You must choose NVs before running this ESR script")
                else:
                    ESR.ESR_map_focus(ApplicationWindow.selected_points, roi_focus, esr_param, ApplicationWindow.esrPlot)

            if script_name == 'ESR (grid)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                if ApplicationWindow.radio_angled_grid.isChecked():
                    points = Meshing.get_points_on_a_grid_angled(pt_a2, pt_b2, xpts, ypts)
                else:
                    points = Meshing.get_points_on_a_grid(pt_a2, pt_b2, xpts, ypts)
                roi_focus = Meshing.two_pts_to_roi(pt_a2, pt_b2)

                esr_param = ESR.ESR_load_param(ApplicationWindow.path_script.text())
                print 'ESR (grid)'
                if not esr_param == {}:
                    ESR.ESR_map_focus(points, roi_focus, esr_param, ApplicationWindow.esrPlot)

            elif script_name == 'ESR (point)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                esr_param = ESR.ESR_load_param(ApplicationWindow.path_script.text())
                roi_focus = Meshing.two_pts_to_roi(pt_a2, pt_b2)
                print 'ESR (point)'
                if not esr_param == {}:
                    ESR.ESR_map([pt_a2], esr_param, ApplicationWindow.esrPlot)

            elif script_name == 'AutoFocus':
                print 'AutoFocus'
                _, pt_a, pt_b, _, _, _, _ = get_pts_and_size(ApplicationWindow)
                roi_focus = Meshing.two_pts_to_roi(pt_a, pt_b)
                af_parameter = AF.AF_load_param(ApplicationWindow.path_script.text())

                if not af_parameter == {}:
                    #voltage_focus = AF.autofocus_RoI(af_parameter, roi_focus)
                    voltage_focus = AF.autofocus_RoI(af_parameter, roi_focus, ApplicationWindow.piezo, focPlot=ApplicationWindow.focPlot, queue=ApplicationWindow.script_queue)
                    ApplicationWindow.statusBar().showMessage('new focus {:0.3f}'.format(voltage_focus),2000)
                    ApplicationWindow.txt_focus_voltage.setText('{:0.2f}'.format(voltage_focus))

            elif script_name == 'AutoFocus (mean)':
                print 'AutoFocus (mean)'
                _, pt_a, pt_b, _, _, _, _ = get_pts_and_size(ApplicationWindow)
                roi_focus = Meshing.two_pts_to_roi(pt_a, pt_b)
                af_parameter = AF.AF_load_param(ApplicationWindow.path_script.text())

                if not af_parameter == {}:
                    #voltage_focus = AF.autofocus_RoI(af_parameter, roi_focus)
                    voltage_focus = AF.autofocus_RoI_mean(af_parameter, roi_focus, ApplicationWindow.piezo, focPlot=ApplicationWindow.focPlot, queue=ApplicationWindow.script_queue)
                    ApplicationWindow.statusBar().showMessage('new focus {:0.3f}'.format(voltage_focus),2000)
                    ApplicationWindow.txt_focus_voltage.setText('{:0.2f}'.format(voltage_focus))

            elif script_name == 'AutoFocus (mean, grid)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                if ApplicationWindow.radio_angled_grid.isChecked():
                    points = Meshing.get_points_on_a_grid_angled(pt_a2, pt_b2, xpts, ypts)
                else:
                    points = Meshing.get_points_on_a_grid(pt_a2, pt_b2, xpts, ypts)
                roi_focus = Meshing.two_pts_to_roi(pt_a2, pt_b2)

                af_parameter = AF.AF_load_param_grid(ApplicationWindow.path_script.text())
                print 'AutoFocus (mean, grid)'
                if not af_parameter == {}:
                    dirpath = af_parameter['AF_path']
                    tag = af_parameter['AF_tag']
                    tag = af_parameter['AF_tag']
                    rw.save_data(points, dirpath, tag + 'ptarray')
                    save_settings_exp(ApplicationWindow, dirpath, tag)
                    AF.autofocus_ROI_mean_map(points, af_parameter, roi_focus, ApplicationWindow.piezo, focPlot=ApplicationWindow.focPlot, queue=ApplicationWindow.script_queue, imPlot=ApplicationWindow.imPlot)


            elif script_name == 'Counter':
                cnts_parameter = Cnts.counter_load_param(ApplicationWindow.path_script.text())
                #counter = Cnts.PlotAPD(sampleRate=float(cnts_parameter['sample_rate']), timePerPt=float(cnts_parameter['time_per_pt']), canvas = ApplicationWindow.esrPlot)
                counter = Cnts.PlotAPD(sampleRate=float(cnts_parameter['sample_rate']), timePerPt=float(cnts_parameter['time_per_pt']), canvas = None)
                counter.startPlot(queue = ApplicationWindow.script_queue)


            elif script_name == 'Get Distance':
                print('Get Distance')
                _, pt_a, pt_b, _, _, _, _ = get_pts_and_size(ApplicationWindow)
                dist_params = rw.load_json(str(ApplicationWindow.path_script.text()))
                roi_focus = {
                    "zo": dist_params['zo'],
                    "dz": dist_params['dz'],
                    "zPts": dist_params['zPts'],
                    "xyPts": dist_params['xyPts']
                }
                roi_a = {
                    "xo": pt_a[0],
                    "yo": pt_a[1],
                    "dx": dist_params['dx'],
                    "dy": dist_params['dy'],
                }
                roi_b = {
                    "xo": pt_b[0],
                    "yo": pt_b[1],
                    "dx": dist_params['dx'],
                    "dy": dist_params['dy'],
                }
                dirpath = dist_params['dirpath']
                tag_a = dist_params['tag_a']
                tag_b = dist_params['tag_b']


                if not dist_params == {}:
                    init_focus = ApplicationWindow.txt_focus_voltage.text()
                    _, voltage_data, y_data = AF.autofocus_RoI(dist_params, roi_a, ApplicationWindow.piezo, return_data=True)
                    rw.save_data([voltage_data,y_data], dirpath, tag_a)
                    _, voltage_data, y_data = AF.autofocus_RoI(dist_params, roi_b, ApplicationWindow.piezo, return_data=True)
                    rw.save_data([voltage_data,y_data], dirpath, tag_b)

                    PC.MDT693B().setVoltage(init_focus)

            elif script_name == 'ZI Frequency Sweep (point)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                ZI_param = ZIControl.ZI_load_param(ApplicationWindow.path_script.text())
                print 'ZI Frequency Sweep (point)'
                if not ZI_param == {}:
                    ZIControl.ZI_map([pt_a2], ZI_param,ApplicationWindow.esrPlot)
                print(ApplicationWindow.esrPlot)



            elif script_name == 'ZI Frequency Sweep (grid)':
                _, pt_a2, pt_b2, _, xpts, ypts, _ = get_pts_and_size(ApplicationWindow)
                points = Meshing.get_points_on_a_grid(pt_a2, pt_b2, xpts, ypts)
                roi_focus = Meshing.two_pts_to_roi(pt_a2, pt_b2)

                ZI_param = ZIControl.ZI_load_param(ApplicationWindow.path_script.text())
                print 'ZI Frequency Sweep (grid)'
                if not ZI_param == {}:
                    ZIControl.ZI_map_focus(points, roi_focus, ZI_param, ApplicationWindow.esrPlot)

            elif script_name == 'reset scan range':

                def is_scan_range_param(myjson):
                    try:
                        json_object = json.loads(myjson)
                    except ValueError, e:
                        return False

                    assert 'pt_1a_x' in json_object.keys()
                    assert 'pt_1a_y' in json_object.keys()
                    assert 'pt_1b_x' in json_object.keys()
                    assert 'pt_1b_y' in json_object.keys()
                    assert 'pt_1_x' in json_object.keys()
                    assert 'pt_1_y' in json_object.keys()
                    return True

                param_txt = str(ApplicationWindow.path_script.text())
                if is_scan_range_param(param_txt):
                    param = json.loads(param_txt)
                else:
                    param = {
                        "pt_1a_x": "-0.4",
                        "pt_1a_y": "-0.4",
                        "pt_1b_x": "0.4",
                        "pt_1b_y": "0.4",
                        "pt_1_x": "120",
                        "pt_1_y": "120"
                    }

                ApplicationWindow.txt_pt_1a_x.setText(param['pt_1a_x'])
                ApplicationWindow.txt_pt_1b_x.setText(param['pt_1b_x'])
                ApplicationWindow.txt_pt_1a_y.setText(param['pt_1a_y'])
                ApplicationWindow.txt_pt_1b_y.setText(param['pt_1b_y'])
                ApplicationWindow.txt_pt_1_x_pts.setText(param['pt_1_x'])
                ApplicationWindow.txt_pt_1_y_pts.setText(param['pt_1_y'])

        def stop_script(ApplicationWindow):
            ApplicationWindow.script_queue.put('STOP')


    ##################################################################################
    # ADD GLOBAL ####################################################################
    ##################################################################################
    def add_global(grid, row_start = 1, column_start =  1):

        ApplicationWindow.button_load_settings = QtGui.QPushButton('load settings', ApplicationWindow.main_widget)
        ApplicationWindow.button_load_settings.clicked.connect(lambda: load_settings(ApplicationWindow))
        grid.addWidget(ApplicationWindow.button_load_settings,row_start,column_start)

        ApplicationWindow.button_save_settings = QtGui.QPushButton('save settings', ApplicationWindow.main_widget)
        ApplicationWindow.button_save_settings.clicked.connect(lambda: save_settings(ApplicationWindow))
        grid.addWidget(ApplicationWindow.button_save_settings,row_start,column_start+1)

        ApplicationWindow.button_exit = QtGui.QPushButton('exit', ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.button_exit,row_start,column_start+2)

        # settings
        ApplicationWindow.cmb_APD = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_APD.addItems(['Use APD', 'Use Diode'])
        # ApplicationWindow.cmb_APD.changeEvent(ApplicationWindow.button_APD)
        # ApplicationWindow.button_APD = QtGui.QPushButton('Use APD',ApplicationWindow.main_widget)
        # ApplicationWindow.button_APD.setCheckable(True)
        # ApplicationWindow.button_APD.setChecked(True)
        # ApplicationWindow.button_APD.clicked.connect(ApplicationWindow.button_APD)
        grid.addWidget(ApplicationWindow.cmb_APD,1,16)

        def choose_setup(setup):
            if setup == 'Warm Setup':
                ApplicationWindow.piezo = 'Z'
            elif setup == 'Cold Setup':
                ApplicationWindow.piezo = 'X'

        def set_img_FW(text):
            print("not yet implemented")

        ApplicationWindow.cmb_img = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_img.addItems(['Fluorescence', 'Reflection'])
        grid.addWidget(ApplicationWindow.cmb_img,1,17)
        ApplicationWindow.cmb_img.activated[str].connect(set_img_FW)


        ApplicationWindow.cmb_setup = QtGui.QComboBox(ApplicationWindow.main_widget)
        ApplicationWindow.cmb_setup.addItems(['Warm Setup', 'Cold Setup'])
        ApplicationWindow.cmb_setup.activated[str].connect(choose_setup)
        grid.addWidget(ApplicationWindow.cmb_setup,1,18)


    ##################################################################################
    # ADD SETTINGS ####################################################################
    ##################################################################################
    def add_settings(grid, row_start = 1, column_start =  1):


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

                elif pt_id == 'c':
                    ApplicationWindow.txt_pt_2c_x.setText(x)
                    ApplicationWindow.txt_pt_2c_y.setText(y)



                ApplicationWindow.imPlot.mpl_disconnect(click_id)
                reset_shapes()


            click_id = ApplicationWindow.imPlot.mpl_connect('button_press_event', clicked_image)


        ApplicationWindow.label_scan_1a = QtGui.QLabel("pt 1a (scan)", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_scan_1a,row_start,column_start)
        ApplicationWindow.label_scan_1b = QtGui.QLabel("pt 1b (scan)", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_scan_1b,row_start+1,column_start)
        ApplicationWindow.label_pts_1 = QtGui.QLabel("# pts 1", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_pts_1,row_start+2,column_start)
        ApplicationWindow.button_scan_2a = QtGui.QPushButton('pt 2a', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan_2a.clicked.connect(lambda: get_image_point('a'))
        grid.addWidget(ApplicationWindow.button_scan_2a,row_start+3,column_start)
        ApplicationWindow.button_scan_2b = QtGui.QPushButton('pt 2b', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan_2b.clicked.connect(lambda: get_image_point('b'))
        # ApplicationWindow.button_scan_2b.clicked.connect(lambda: ApplicationWindow.imPlot.mpl_connect('button_press_event', lambda x: get_image_point(x, 'b')))
        grid.addWidget(ApplicationWindow.button_scan_2b,row_start+4,column_start)
        ApplicationWindow.button_scan_2c = QtGui.QPushButton('pt 2c', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan_2c.clicked.connect(lambda: get_image_point('c'))
        # ApplicationWindow.button_scan_2b.clicked.connect(lambda: ApplicationWindow.imPlot.mpl_connect('button_press_event', lambda x: get_image_point(x, 'b')))
        grid.addWidget(ApplicationWindow.button_scan_2c,row_start+5,column_start)
        ApplicationWindow.label_pts_2 = QtGui.QLabel("# pts 2", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_pts_2,row_start+6,column_start)
        ApplicationWindow.label_laser = QtGui.QLabel("laser", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_laser,row_start+7,column_start)

        ApplicationWindow.label_x = QtGui.QLabel("x", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_x,row_start-1,column_start+1)
        ApplicationWindow.txt_pt_1a_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1a_x,row_start,column_start+1)
        ApplicationWindow.txt_pt_1b_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1b_x,row_start+1,column_start+1)
        ApplicationWindow.txt_pt_1_x_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1_x_pts,row_start+2,column_start+1)
        ApplicationWindow.txt_pt_2a_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2a_x,row_start+3,column_start+1)
        ApplicationWindow.txt_pt_2b_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2b_x,row_start+4,column_start+1)
        ApplicationWindow.txt_pt_2c_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2c_x,row_start+5,column_start+1)
        ApplicationWindow.txt_pt_2_x_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2_x_pts,row_start+6,column_start+1)
        ApplicationWindow.txt_pt_laser_x = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_laser_x,row_start+7,column_start+1)

        ApplicationWindow.label_y = QtGui.QLabel("y", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_y,row_start-1,column_start+2)
        ApplicationWindow.txt_pt_1a_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1a_y,row_start,column_start+2)
        ApplicationWindow.txt_pt_1b_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1b_y,row_start+1,column_start+2)
        ApplicationWindow.txt_pt_1_y_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_1_y_pts,row_start+2,column_start+2)
        ApplicationWindow.txt_pt_2a_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2a_y,row_start+3,column_start+2)
        ApplicationWindow.txt_pt_2b_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2b_y,row_start+4,column_start+2)
        ApplicationWindow.txt_pt_2c_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2c_y,row_start+5,column_start+2)
        ApplicationWindow.txt_pt_2_y_pts = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_2_y_pts,row_start+6,column_start+2)
        ApplicationWindow.txt_pt_laser_y = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_pt_laser_y,row_start+7,column_start+2)

        ApplicationWindow.button_set_laser = QtGui.QPushButton('set laser', ApplicationWindow.main_widget)
        ApplicationWindow.button_set_laser.clicked.connect(lambda : set_laser(None))
        grid.addWidget(ApplicationWindow.button_set_laser,row_start+3,column_start+3)


        ApplicationWindow.label_time_per_pt = QtGui.QLabel("time per pt", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_time_per_pt,row_start,column_start+3)
        ApplicationWindow.txt_time_per_pt = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_time_per_pt,row_start+1,column_start+3)

        ApplicationWindow.label_focus_voltage = QtGui.QLabel('Focus Piezo Voltage', ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_focus_voltage, row_start + 4, column_start + 3)
        ApplicationWindow.txt_focus_voltage = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_focus_voltage, row_start + 5, column_start + 3)
        ApplicationWindow.button_set_voltage = QtGui.QPushButton('Set Piezo Voltage', ApplicationWindow.main_widget)
        ApplicationWindow.button_set_voltage.clicked.connect(lambda: f.set_focus(ApplicationWindow.piezo, float(ApplicationWindow.txt_focus_voltage.text())))
        grid.addWidget(ApplicationWindow.button_set_voltage,row_start+6,column_start+3)

        ApplicationWindow.radio_angled_grid = QtGui.QCheckBox("Angled Grid")
        ApplicationWindow.radio_angled_grid.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_angled_grid, row_start+2, column_start+3)

        ApplicationWindow.button_copy_scan_params = QtGui.QPushButton("Copy Scan Parameters")
        ApplicationWindow.button_copy_scan_params.clicked.connect(copy_scan_params)
        grid.addWidget(ApplicationWindow.button_copy_scan_params, row_start-1, column_start+3)
# ApplicationWindow.RS = RectangleSelector(ApplicationWindow.imPlot.axes, ApplicationWindow.select_RoI, button = 3, drawtype='box', rectprops = rectprops)


    ##################################################################################
    # ADD DISPLAY ####################################################################
    ##################################################################################
    def add_display(grid, row_start = 1, column_start =  1):

        def execute_scan():

            remove_patches(ApplicationWindow)

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
            if ApplicationWindow.radio_distconv.isChecked():
                dist_volt_conv = ApplicationWindow.txt_distconv.text()
            else:
                dist_volt_conv = None
            ApplicationWindow.imageData, ApplicationWindow.imageRoI = DeviceTriggers.scanGui(ApplicationWindow.imPlot,xMin,xMax,pts_x,yMin,yMax,pts_y,timePerPt, ApplicationWindow.scan_queue, bool_use_apd, dist_volt_conv)

            set_laser([0, 0])

            ApplicationWindow.statusBar().clearMessage()
            reset_shapes()
            # if(ApplicationWindow.autosaveCheck.isChecked() == True):
            #     ApplicationWindow.saveImageClicked()
        def interrupt_scan():
            ApplicationWindow.scan_queue.put('STOP')

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

        ApplicationWindow.patches = []
        ApplicationWindow.nv_points = []
        ApplicationWindow.selected_points = []

        ApplicationWindow.radio_roi = QtGui.QCheckBox("&region of interest (RoI)")
        ApplicationWindow.radio_roi.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_roi,row_start, column_start)
        ApplicationWindow.radio_NVs = QtGui.QCheckBox("selected NVs")
        ApplicationWindow.radio_NVs.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_NVs,row_start, column_start+1)
        ApplicationWindow.radio_NV_labels = QtGui.QCheckBox("NV labels")
        ApplicationWindow.radio_NV_labels.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_NV_labels,row_start+1, column_start)
        ApplicationWindow.radio_grid = QtGui.QCheckBox("Grid")
        ApplicationWindow.radio_grid.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_grid,row_start +2, column_start)
        ApplicationWindow.radio_line = QtGui.QCheckBox("Line")
        ApplicationWindow.radio_line.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_line,row_start +3, column_start)
        ApplicationWindow.radio_pt2 = QtGui.QCheckBox("pt 2a")
        ApplicationWindow.radio_pt2.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_pt2,row_start +4, column_start)
        ApplicationWindow.radio_laser = QtGui.QCheckBox("Laser")
        ApplicationWindow.radio_laser.clicked.connect(reset_shapes)
        grid.addWidget(ApplicationWindow.radio_laser,row_start +5, column_start)
        ApplicationWindow.radio_distconv= QtGui.QCheckBox("Convert to Distance")
        grid.addWidget(ApplicationWindow.radio_distconv,row_start +4, column_start+1)
        ApplicationWindow.txt_distconv = QtGui.QLineEdit()
        grid.addWidget(ApplicationWindow.txt_distconv,row_start +5, column_start+1)

        # set RoI and zoom
        ApplicationWindow.button_zoom_in_RoI = QtGui.QPushButton('zoom in (RoI)',ApplicationWindow.main_widget)
        ApplicationWindow.button_zoom_in_RoI.clicked.connect(zoom_RoI_in)
        grid.addWidget(ApplicationWindow.button_zoom_in_RoI,row_start,column_start+2)
        ApplicationWindow.button_zoom_out_RoI = QtGui.QPushButton('zoom out', ApplicationWindow.main_widget)
        ApplicationWindow.button_zoom_out_RoI.clicked.connect(zoom_RoI_out)
        grid.addWidget(ApplicationWindow.button_zoom_out_RoI,row_start,column_start+3)

        # color bar
        def cbarThreshClicked(self):
            remove_patches(ApplicationWindow)
            xMin, xMax, yMin, yMax = get_min_max(ApplicationWindow)
            DeviceTriggers.updateColorbar(ApplicationWindow.imageData, ApplicationWindow.imPlot, [xMin, xMax, yMin, yMax], float(ApplicationWindow.cbar_max.text()))
            display_shapes()

        ApplicationWindow.cbar_max = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.cbar_max,row_start +6, column_start)
        ApplicationWindow.label_cbar_max = QtGui.QLabel("Colorbar Threshold", ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.label_cbar_max,row_start +6, column_start +1)
        ApplicationWindow.button_cbar_thresh = QtGui.QPushButton('Update Colorbar', ApplicationWindow.main_widget)
        ApplicationWindow.button_cbar_thresh.clicked.connect(cbarThreshClicked)
        grid.addWidget(ApplicationWindow.button_cbar_thresh,row_start +6, column_start +2)

        ApplicationWindow.button_stop = QtGui.QPushButton('Stop Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_stop.clicked.connect(interrupt_scan)
        grid.addWidget(ApplicationWindow.button_stop,row_start +7,column_start+1)
        ApplicationWindow.button_scan = QtGui.QPushButton('Scan', ApplicationWindow.main_widget)
        ApplicationWindow.button_scan.clicked.connect(execute_scan)
        grid.addWidget(ApplicationWindow.button_scan,row_start +7,column_start)

        # save image
        def write_image(array, dirpath, tag, columns = None):
            df = pd.DataFrame(array, columns = columns)
            if(columns == None):
                header = False
            else:
                header = True
            start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
            filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
            filepathJPG = dirpath + "\\" + start_time + '_' + tag + '.jpg'
            # filepathCSV = dirpath + filename + '.csv'
            # filepathJPG = dirpath + filename + '.jpg'
            df.to_csv(filepathCSV, index = False, header=header)
            ApplicationWindow.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')
            ApplicationWindow.statusBar().showMessage("Image Data Saved",2000)

        ApplicationWindow.txt_save_image_location = gui_cw.FileBoxSave('Z://Lab//Cantilever//Measurements//')
        grid.addWidget(ApplicationWindow.txt_save_image_location, row_start + 8, column_start)
        ApplicationWindow.txt_save_image_tag = QtGui.QLineEdit(ApplicationWindow.main_widget)
        grid.addWidget(ApplicationWindow.txt_save_image_tag, row_start + 8, column_start + 1)
        ApplicationWindow.button_save_image = QtGui.QPushButton('Save Image', ApplicationWindow.main_widget)
        ApplicationWindow.button_save_image.clicked.connect(lambda: write_image(ApplicationWindow.imageData, str(ApplicationWindow.txt_save_image_location.text()), str(ApplicationWindow.txt_save_image_tag.text())))
        grid.addWidget(ApplicationWindow.button_save_image, row_start + 8, column_start + 2)




        ApplicationWindow.scan_queue = Queue.Queue()
        ApplicationWindow.script_queue = Queue.Queue()


    def add_choosing_points(grid, row_start = 1, column_start =  1):

        # def run_esr(ApplicationWindow):
        #     nv_locs = numpy.array(pd.read_csv(str(ApplicationWindow.esrReadLoc.text()) + '.csv', header = None))
        #     print(nv_locs)
        #     print(len(nv_locs))
        #     img_baseline = numpy.array(pd.read_csv(str(ApplicationWindow.esrReadLoc.text()) + 'baselineimg.csv'))
        #     ApplicationWindow.loadRoI(str(ApplicationWindow.esrReadLoc.text()) + '.roi')
        #     esr_num = 0
        #     RF_Power = -12
        #     avg = 100
        #     while esr_num < len(nv_locs):
        #         print(esr_num)
        #
        #         ApplicationWindow.statusBar().showMessage("Focusing", 0)
        #         zo = float(ApplicationWindow.zPos.text())
        #         dz = float(ApplicationWindow.zRange.text())
        #         zPts = float(ApplicationWindow.zPts.text())
        #         xyPts = float(ApplicationWindow.xyRange.text())
        #         zMin, zMax = zo - dz/2., zo + dz/2.
        #         roi_focus = ApplicationWindow.RoI.copy()
        #         roi_focus['dx'] = .005
        #         roi_focus['dy'] = .005
        #         roi_focus['xo'] = nv_locs[0][0]
        #         roi_focus['yo'] = nv_locs[0][1]
        #         roi_focus['xPts'] = xyPts
        #         roi_focus['yPts'] = xyPts
        #         print roi_focus
        #         voltage_focus = focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = roi_focus)
        #         ApplicationWindow.zPos.setText('{:0.4f}'.format(voltage_focus))
        #         ApplicationWindow.statusBar().clearMessage()
        #         plt.close()
        #
        #
        #         ApplicationWindow.statusBar().showMessage("Scanning and Correcting for Shift", 0)
        #         xmin, xmax, ymin, ymax = roi_to_min_max(ApplicationWindow.RoI)
        #         img_new, ApplicationWindow.imageRoI = DeviceTriggers.scanGui(ApplicationWindow.imPlot, xmin, xmax, ApplicationWindow.RoI['xPts'], ymin, ymax, ApplicationWindow.RoI['xPts'], .001)
        #         shift = track.corr_NVs(img_baseline, img_new)
        #         print(shift)
        #         ApplicationWindow.RoI = track.update_roi(ApplicationWindow.RoI, shift)
        #         nv_locs = track.shift_points_v(nv_locs, ApplicationWindow.RoI, shift)
        #         xmin, xmax, ymin, ymax = roi_to_min_max(ApplicationWindow.RoI)
        #         ApplicationWindow.imPlot.axes.set_xlim(left= xmin, right =xmax)
        #         ApplicationWindow.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
        #         img_new, ApplicationWindow.imageRoI = DeviceTriggers.scanGui(ApplicationWindow.imPlot, xmin, xmax, ApplicationWindow.RoI['xPts'], ymin, ymax, ApplicationWindow.RoI['xPts'], .001)
        #         ApplicationWindow.statusBar().clearMessage()
        #         for pt in nv_locs:
        #             circ = patches.Circle((pt[0], pt[1]), .01*min(ApplicationWindow.RoI['dx'],ApplicationWindow.RoI['dy']), fc = 'b')
        #             ApplicationWindow.imPlot.axes.add_patch(circ)
        #
        #         nv_locs = track.locate_shifted_NVs(img_new, nv_locs, ApplicationWindow.RoI)
        #         for pt in nv_locs:
        #             circ = patches.Circle((pt[0], pt[1]), .01*min(ApplicationWindow.RoI['dx'],ApplicationWindow.RoI['dy']), fc = 'r')
        #             ApplicationWindow.imPlot.axes.add_patch(circ)
        #         ApplicationWindow.imPlot.draw()
        #         pt = nv_locs[esr_num]
        #
        #         if(pt[0] == 0 and pt[1] == 0): # failed to find matching NV in shifted frame
        #             esr_num += 1
        #             continue
        #         ApplicationWindow.statusBar().showMessage("Running ESR", 0)
        #         test_freqs = numpy.linspace(2820000000, 2920000000, 200)
        #         esr_data, fit_params, fig = ESR.run_esr(RF_Power, test_freqs, pt, num_avg=avg, int_time=.002)
        #         dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150712_GuiTest'
        #         tag = 'NV{:00d}_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(esr_num, RF_Power, avg)
        #         ESR.save_esr(esr_data, fig, dirpath, tag)
        #         esr_num += 1
        #         ApplicationWindow.statusBar().clearMessage()
        #
        #     ApplicationWindow.circ = None
        #     ApplicationWindow.rect = None


        ApplicationWindow.is_choosing_points = False

        # select NVs
        ApplicationWindow.button_select_NVs = QtGui.QPushButton('select NV',ApplicationWindow.main_widget)
        ApplicationWindow.button_select_NVs.setCheckable(True)
        ApplicationWindow.button_select_NVs.setChecked(False)
        ApplicationWindow.button_select_NVs.clicked.connect(lambda: choosing_points(ApplicationWindow))
        grid.addWidget(ApplicationWindow.button_select_NVs,row_start,column_start)



    def add_test(grid):
        txt_boxes = {'text1': None, 'text2':None}
        for i, x in enumerate(txt_boxes):
            txt_boxes.update({x:QtGui.QLineEdit(ApplicationWindow.main_widget)})
            grid.addWidget(txt_boxes[x], 5+i, 5)

        # for name in txt_names:
        #     ApplicationWindow.txt_boxes.update{''} = QtGui.QLineEdit(ApplicationWindow.main_widget)
        #     grid.addWidget(ApplicationWindow.txt_test, 5, 5)
    ##################################################################################
    ##### GRID IMAGE #################################################################
    ##################################################################################
    # ApplicationWindow.grid_image = QtGui.QGridLayout()
    # vbox_main.addLayout(ApplicationWindow.grid_image)

    ApplicationWindow.imPlot = gui_cw.MyMplCanvas(ApplicationWindow.main_widget, width=5, height=4, dpi=100)
    plotBox.addWidget(ApplicationWindow.imPlot)
    ApplicationWindow.focPlot = gui_cw.MyMplCanvas(ApplicationWindow.main_widget, width=5, height=4, dpi=100)
    plotBox.addWidget(ApplicationWindow.focPlot)
    ApplicationWindow.esrPlot = gui_cw.MyMplCanvas(ApplicationWindow.main_widget, width=5, height=4, dpi=100)
    plotBox.addWidget(ApplicationWindow.esrPlot)

    #ApplicationWindow.imageData = None
    ApplicationWindow.imageData = np.array(Image.open('C:\\Users\\Experiment\\Desktop\\GuiIcons\\beaker.jpg'))
    ApplicationWindow.imPlot.axes.imshow(ApplicationWindow.imageData)
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

    add_settings(ApplicationWindow.grid_settings)



    ##### display #################################################################################################
    ApplicationWindow.group_display = QtGui.QGroupBox("Display")
    # ApplicationWindow.group_display.isCheckable()
    ApplicationWindow.grid_display = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_display,1,2)
    ApplicationWindow.group_display.setLayout(ApplicationWindow.grid_display)

    add_display(ApplicationWindow.grid_display)
    add_choosing_points(ApplicationWindow.grid_display, row_start = 2, column_start =  3)

    ApplicationWindow.plot_nvs = False


    ##### execute #################################################################################################
    ApplicationWindow.group_execute = QtGui.QGroupBox("Execute")
    ApplicationWindow.grid_execute = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_execute,2,1)
    ApplicationWindow.group_execute.setLayout(ApplicationWindow.grid_execute)

    add_execute(ApplicationWindow.grid_execute)
    # add_test(ApplicationWindow.grid_execute)

    ##### global #################################################################################################
    ApplicationWindow.group_global = QtGui.QGroupBox("global")
    ApplicationWindow.grid_global = QtGui.QGridLayout()
    ApplicationWindow.grid_controls.addWidget(ApplicationWindow.group_global,2,2)
    ApplicationWindow.group_global.setLayout(ApplicationWindow.grid_global)

    add_global(ApplicationWindow.grid_global)


    ApplicationWindow.zoomed_in = False
    load_settings(ApplicationWindow, 'Z://Lab//Cantilever//Measurements//default.set')

    reset_shapes()
    QtGui.QApplication.processEvents()


def load_settings(ApplicationWindow, filename = None):

    def dict_to_values_settings(ApplicationWindow, dict):
        ApplicationWindow.txt_pt_1a_x.setText(dict['pt_1a_x'])
        ApplicationWindow.txt_pt_1b_x.setText(dict['pt_1b_x'])
        ApplicationWindow.txt_pt_2a_x.setText(dict['pt_2a_x'])
        ApplicationWindow.txt_pt_2b_x.setText(dict['pt_2b_x'])
        ApplicationWindow.txt_pt_2c_x.setText(dict['pt_2c_x'])
        ApplicationWindow.txt_pt_1a_y.setText(dict['pt_1a_y'])
        ApplicationWindow.txt_pt_1b_y.setText(dict['pt_1b_y'])
        ApplicationWindow.txt_pt_2a_y.setText(dict['pt_2a_y'])
        ApplicationWindow.txt_pt_2b_y.setText(dict['pt_2b_y'])
        ApplicationWindow.txt_pt_2c_y.setText(dict['pt_2c_y'])
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

        ApplicationWindow.parameters_paths_scripts = dict['parameters_paths_script']
        print ApplicationWindow.parameters_paths_scripts
        ApplicationWindow.cmb_execute.setCurrentIndex(ApplicationWindow.cmb_execute.findText(dict['selected_script']))
        ApplicationWindow.path_script.setText(dict['parameters_paths_script'][dict['selected_script']])





    def dict_to_values_global(ApplicationWindow, dict):
        ApplicationWindow.cmb_APD.setCurrentIndex(ApplicationWindow.cmb_APD.findText(dict['selected_detector']))
        ApplicationWindow.cmb_setup.setCurrentIndex(ApplicationWindow.cmb_setup.findText(dict['selected_setup']))

        def choose_setup(setup):
            if setup == 'Warm Setup':
                ApplicationWindow.piezo = 'Z'
            elif setup == 'Cold Setup':
                ApplicationWindow.piezo = 'X'

        choose_setup(dict['selected_setup'])
        #ApplicationWindow.txt_focus_voltage.setText(str(PC.MDT693A('Z').getVoltage()))




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
            "pt_2c_x": str(ApplicationWindow.txt_pt_2c_x.text()),
            "pt_1a_y": str(ApplicationWindow.txt_pt_1a_y.text()),
            "pt_1b_y": str(ApplicationWindow.txt_pt_1b_y.text()),
            "pt_2a_y": str(ApplicationWindow.txt_pt_2a_y.text()),
            "pt_2b_y": str(ApplicationWindow.txt_pt_2b_y.text()),
            "pt_2c_y": str(ApplicationWindow.txt_pt_2c_y.text()),
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
            "selected_detector": str(ApplicationWindow.cmb_APD.currentText()),
            "selected_setup": str(ApplicationWindow.cmb_setup.currentText())
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

def save_settings_exp(ApplicationWindow, dirpath, tag):
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    filename = '\\' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second  +'-' + str(tag)
    filepath = dirpath + filename + '.set'
    save_settings(ApplicationWindow, set_filename=filepath)


def get_pts_and_size(ApplicationWindow, ptID = '2'):
    if ptID == '1':
        pt_a = [float(ApplicationWindow.txt_pt_1a_x.text()), float(ApplicationWindow.txt_pt_1a_y.text())]
        pt_b = [float(ApplicationWindow.txt_pt_1b_x.text()), float(ApplicationWindow.txt_pt_1b_y.text())]
        pt_c = [0,0]
        xpts = float(ApplicationWindow.txt_pt_1_x_pts.text())
        ypts = float(ApplicationWindow.txt_pt_1_y_pts.text())
    elif ptID == '2':
        pt_a = [float(ApplicationWindow.txt_pt_2a_x.text()), float(ApplicationWindow.txt_pt_2a_y.text())]
        pt_b = [float(ApplicationWindow.txt_pt_2b_x.text()), float(ApplicationWindow.txt_pt_2b_y.text())]
        pt_c = [float(ApplicationWindow.txt_pt_2c_x.text()), float(ApplicationWindow.txt_pt_2c_y.text())]
        xpts = float(ApplicationWindow.txt_pt_2_x_pts.text())
        ypts = float(ApplicationWindow.txt_pt_2_y_pts.text())
    pt_L = [float(ApplicationWindow.txt_pt_laser_x.text()), float(ApplicationWindow.txt_pt_laser_y.text())]
    xrange = ApplicationWindow.imPlot.axes.get_xlim()[1]-ApplicationWindow.imPlot.axes.get_xlim()[0]
    yrange = ApplicationWindow.imPlot.axes.get_ylim()[1]-ApplicationWindow.imPlot.axes.get_ylim()[0]
    size= .01*min(xrange,yrange)

    return size, pt_a, pt_b, pt_c, xpts, ypts, pt_L

def get_min_max(ApplicationWindow):
    pta_x = float(ApplicationWindow.txt_pt_1a_x.text())
    ptb_x = float(ApplicationWindow.txt_pt_1b_x.text())
    pta_y = float(ApplicationWindow.txt_pt_1a_y.text())
    ptb_y = float(ApplicationWindow.txt_pt_1b_y.text())

    xMin = min([pta_x, ptb_x])
    xMax = max([pta_x, ptb_x])
    yMin = min([pta_y, ptb_y])
    yMax = max([pta_y, ptb_y])

    return xMin, xMax, yMin, yMax


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

