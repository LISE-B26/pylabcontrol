import yaml, json


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

def save_b26_file(filename, instruments = None, scripts = None, probes = None):
    """
    save instruments, scripts and probes as a json file
    Args:
        filename:
        instruments:
        scripts:
        probes:

    Returns:

    """

    data_dict = {}
    if instruments is not None:
        data_dict['instruments'] = instruments
    if scripts is not None:
        data_dict['scripts'] = scripts
    if probes is not None:
        data_dict['probes'] = probes

    if data_dict != {}:
        with open(filename, 'w') as outfile:
            tmp = json.dump(data_dict, outfile, indent=4)



if __name__ == '__main__':
    instruments = {
        # 'inst_dummy': 'DummyInstrument',
        'zihf2': 'ZIHF2',
        'pressure gauge': 'PressureGauge',
        'cryo station': 'CryoStation',
        'spectrum analyzer': 'SpectrumAnalyzer',
        'microwave generator': 'MicrowaveGenerator'
    }

    scripts = {

        'u-wave spectra': {
            'script_class': 'KeysightGetSpectrum',
            'instruments': {
                'spectrum_analyzer': 'spectrum analyzer'
            }
        },

        'u-wave spectra vs power': {
            'script_class': 'MWSpectraVsPower',
            'instruments': {
                'cryo_station': 'cryo station',
                'spectrum_analyzer': 'spectrum analyzer',
                'microwave_generator': 'microwave generator'
            }
        },

        # 'u-wave spectra vs power': {
        #     'script_class': 'MWSpectraVsPower',
        #     'instruments':{
        #     'microwave_generator' : 'microwave generator',
        #     'cryo_station' : 'cryo station',
        #     'spectrum_analyzer' : 'spectrum analyzer'
        #     }
        # },

        'ZI sweep': {
            'script_class': 'ZISweeper',
            'instruments': {'zihf2': 'zihf2'}
        },

        'High res scan': {
            'script_class': 'ZISweeperHighResolution',
            'scripts': {
                'zi sweep': {
                    'script_class': 'ZISweeper',
                    'instruments': {'zihf2': 'zihf2'}
                }
            }
        }

    }

    probes = {
        # 'random': {'probe_name': 'value1', 'instrument_name': 'inst_dummy'},
        # 'value2': {'probe_name': 'value2', 'instrument_name': 'inst_dummy'},
        'ZI (R)': {'probe_name': 'R', 'instrument_name': 'zihf2'},
        'ZI (X)': {'probe_name': 'X', 'instrument_name': 'zihf2'},
        'T (platform)': {'probe_name': 'platform_temp', 'instrument_name': 'cryo station'},
        'T (stage 1)': {'probe_name': 'stage_1_temp', 'instrument_name': 'cryo station'},
        'T (stage 2)': {'probe_name': 'stage_2_temp', 'instrument_name': 'cryo station'}
        # 'Chamber Pressure' : { 'probe_name': 'pressure', 'instrument_name': 'pressure gauge'}
    }





    filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\a.b26"
    save_b26_file(filename, instruments, scripts, probes)

    # filename = 'C:\\Users\\Experiment\\gui_settings.b26gui'

    data = load_b26_file(filename)

    print(data['instruments'])

    #
    #
    # import yaml
    # in_file_name = "Z:\Lab\Cantilever\Measurements\\tmp_\\a"
    # with open(in_file_name, 'r') as infile:
    #     in_data = yaml.safe_load(infile)
    #
    # instruments = in_data['instruments']
    # scripts = in_data['scripts']
    # probes = in_data['probes']
    #
    #
    #
    # inst = load_instruments(instruments)
    #
    # sc = load_scripts(scripts, inst)
    #
    # pr = load_probes(probes, inst)