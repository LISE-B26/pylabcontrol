
from PyLabControl.src.gui.qt_b26_gui import ControlMainWindow
from PyLabControl.src.gui.gui_future_b26_toolkit.b26_load_dialog import LoadDialogB26




class ControlMainWindowB26(ControlMainWindow):

    startup_msg = '\n\n\
    ======================================================\n\
    =============== Starting B26 toolkit  =============\n\
    ======================================================\n\n'

    def __init__(self, filename=None):

        super(ControlMainWindowB26, self).__init__(filename)

    def load_scripts(self):
        """
        opens file dialog to load scripts into gui
        """

        # update scripts so that current settings do not get lost
        for index in range(self.tree_scripts.topLevelItemCount()):
            script_item = self.tree_scripts.topLevelItem(index)
            self.update_script_from_item(script_item)

        dialog = LoadDialogB26(elements_type="scripts", elements_old=self.scripts,
                            filename=self.gui_settings['scripts_folder'])
        if dialog.exec_():
            self.gui_settings['scripts_folder'] = str(dialog.txt_probe_log_path.text())
            scripts = dialog.getValues()
            added_scripts = set(scripts.keys()) - set(self.scripts.keys())
            removed_scripts = set(self.scripts.keys()) - set(scripts.keys())

            if 'data_folder' in self.gui_settings.keys() and os.path.exists(self.gui_settings['data_folder']):
                data_folder_name = self.gui_settings['data_folder']
            else:
                data_folder_name = None

            # create instances of new instruments/scripts
            self.scripts, loaded_failed, self.instruments = Script.load_and_append(
                script_dict={name: scripts[name] for name in added_scripts},
                scripts=self.scripts,
                instruments=self.instruments,
                log_function=self.log,
                data_path=data_folder_name)
            # delete instances of new instruments/scripts that have been deselected
            for name in removed_scripts:
                del self.scripts[name]