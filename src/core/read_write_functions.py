import yaml, json
import os


def get_dll_config_path(dll_name, path_to_file='dll_config.txt'):
    """
    gets the path to the dll for the dll dll_name from path_to_file
    Args:
        dll_name:
        path_to_file:

    Returns: path to dll

    """

    # if the function is called from gui then the file has to be located with respect to the gui folder
    if not os.path.isfile(path_to_file):
        path_to_file = os.path.join('../instruments/', path_to_file)

    if not os.path.isfile(path_to_file):
        raise IOError('{:s}: config file is not valid'.format(path_to_file))

    f = open(path_to_file, 'r')
    s = f.read()

    if dll_name[-1] is not ':':
        dll_name += ':'

    config_path = [line.split(dll_name)[1] for line in s.split('\n') if len(line.split(dll_name)) > 1][0].strip()

    if not os.path.isfile(config_path):
        raise IOError('{:s}: config file is not valid'.format(config_path))

    return config_path

def load_b26_file(file_name):
    """
    loads a .b26 file into a dictionary

    Args:
        file_name:

    Returns: dictionary with keys instrument, scripts, probes

    """
    # file_name = "Z:\Lab\Cantilever\Measurements\\tmp_\\a"

    assert os.path.exists(file_name)

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
        probes: dictionary of the form {instrument_name : probe_1_of_intrument, probe_2_of_intrument, ...}

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
        probe_instruments = probes.keys()
        if 'probes' in data_dict:
            # all the instruments required for old and new probes
            probe_instruments= set(probe_instruments + data_dict['probes'].keys())
        else:
            data_dict.update({'probes':{}})

        for instrument in probe_instruments:
            if instrument in data_dict['probes'] and instrument in probes:
                # update the data_dict
                data_dict['probes'][instrument] = ','.join(set(data_dict['probes'][instrument].split(',') + probes[instrument].split(',')))
            else:
                data_dict['probes'].update(probes)


    if data_dict != {}:

        # create folder if it doesn't exist
        if os.path.exists(os.path.dirname(filename)) is False:
            print('creating', os.path.dirname(filename))
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as outfile:
            tmp = json.dump(data_dict, outfile, indent=4)
