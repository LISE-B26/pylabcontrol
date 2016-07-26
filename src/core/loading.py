from PyLabControl.src.core.probe import Probe

def instantiate_probes(probes, instruments):
    """
     Creates instances of the probes inputed;

     Args:
         probes: probes is a nested dictionary with
            (key, sub_dict ) = (name of the probe, {'probe_name': value_probe, 'instrument_name': value_inst}),
            where value_probe is a valid name of a probe in intrument with name value_inst
         for example script = {'detector signal': {'probe_name': "AI0", 'instrument_name': "my_DAQ"}}

     Returns:
         a dictionary with (key,sub_dict) = (name of probe, reference to probe) for all of the probes
         passed to the function that were successfully imported and initialized. Otherwise, probes are omitted
         in the outputted list.

     """

    probe_instances = {}
    for name, sub_dict in probes.iteritems():
        assert isinstance(sub_dict, dict)
        assert "probe_name" in sub_dict
        assert "instrument_name" in sub_dict

        probe_name = sub_dict['probe_name']
        instrument_name = sub_dict['instrument_name']

        if "probe_info" in sub_dict:
            probe_info = sub_dict['probe_info']
        else:
            probe_info = ''

        assert instrument_name in instruments, "{:s} not in {:s}".format(instrument_name, instruments.keys())
        assert probe_name in instruments[instrument_name]._PROBES

        probe_instances.update({name: Probe(instruments[instrument_name], probe_name, name, probe_info)})

    return probe_instances




if __name__ == '__main__':

# ======= test  instantiate_scripts =====
    from src.core.read_write_functions import load_b26_file
    filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XX.b26"
    data = load_b26_file(filename)

    print(data['scripts'])
    instruments = {}
    scripts = instantiate_scripts(data['scripts'], instruments)
    print(scripts)


# # ======= test  instantiate_instruments =====
#     from src.core.read_write_functions import load_b26_file
#     filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XX.b26"
#     data = load_b26_file(filename)
#
#     print(data['instruments'])
#
#     instruments = instantiate_instruments(data['instruments'])
#     print(instruments)
