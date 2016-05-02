import yaml, json
import os

def load_b26_file(file_name):
    """
    loads a .b26 file into a dictionary

    Args:
        file_name:

    Returns: dictionary with keys instrument, scripts, probes

    """
    # file_name = "Z:\Lab\Cantilever\Measurements\\tmp_\\a"
    with open(file_name, 'r') as infile:
        data = yaml.safe_load(infile)
    return data

def save_b26_file(filename, instruments = None, scripts = None, probes = None, overwrite = False):
    """
    save instruments, scripts and probes as a json file
    Args:
        filename:
        instruments:
        scripts:
        probes:

    Returns:

    """

    # if overwrite is false load existing data and append to new instruments
    if os.path.isfile(filename) and overwrite == False:
        data_dict = load_b26_file(filename)
    else:
        data_dict = {}

    if instruments is not None:
        if 'instruments' in data_dict:
            data_dict['instruments'].update(instruments)
        else:
            data_dict['instruments'] = instruments
    if scripts is not None:
        if 'scripts' in data_dict:
            data_dict['scripts'].update(scripts)
        else:
            data_dict['scripts'] = scripts
    if probes is not None:
        if 'probes' in data_dict:
            data_dict['probes'].update(probes)
        else:
            data_dict['probes'] = probes


        data_dict['instruments'].update(data_dict['instruments'])
    if 'scripts' in data_dict:
        data_dict['scripts'].update(data_dict['scripts'])
    if 'probes' in data_dict:
        data_dict['probes'].update(data_dict['probes'])

    if data_dict != {}:
        with open(filename, 'w') as outfile:
            tmp = json.dump(data_dict, outfile, indent=4)

def export_default_instruments(filename):
    import src.instruments as instruments
    import inspect

    for name, obj in inspect.getmembers(instruments):
        if inspect.isclass(obj):
            try:
                instrument = obj()
                instrument.save(filename)
            except:
                print('failed to create instrument file for: {:s}'.format(obj.__name__))


def export_default_scripts(filename):
    import src.scripts as scripts
    import inspect

    for name, obj in inspect.getmembers(scripts):
        if inspect.isclass(obj):
            try:
                scripts = obj()
                scripts.save(filename)
            except:
                print('failed to create scripts file for: {:s}'.format(obj.__name__))

if __name__ == '__main__':
    export_default_instruments('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\scripts_and_instruments.b26')
    export_default_scripts('C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\scripts_and_instruments.b26')