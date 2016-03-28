from src.core import Script, Parameter
import os
import pandas as pd


class SaveScriptData(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data')
    ])

    _INSTRUMENTS = {}

    def __init__(self, script, name = None, settings = None):
        Script.__init__(self, name, settings)

        assert isinstance(script, Script)


        self.script = script

    def save(self):
        """
        saves self.data
        """

        path = self.settings['path']
        tag = self.settings['tag']
        data = self.script.data

        if os.path.exists(path) == False:
            os.makedirs(path)

        if len(set([len(v) for k, v in data.iteritems()]))==1:
            # if all entries of the dictionary are the same length we can write the data into a single file
            file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                path,
                self.script.end_time.strftime('%y%m%d-%H_%M_%S'),
                tag,
                'dat'
            )

            df = pd.DataFrame(data)
            df.to_csv(file_path)

        else:
            # otherwise, we write each entry into a separate file into a subfolder data

            path = "{:s}\\data\\".format(path)
            if os.path.exists(path) == False:
                os.makedirs(path)
            for key, value in self.script.data.iteritems():


                file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                    path,
                    self.script.end_time.strftime('%y%m%d-%H_%M_%S'),
                    tag,
                    key
                )

                df = pd.DataFrame(value)
                df.to_csv(file_path)










