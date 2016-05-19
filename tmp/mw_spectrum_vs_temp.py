from src.instruments.spectrum_analyzer import SpectrumAnalyzer
from legacy_src.old_hardware_modules.Cryostation import TemperatureData
import time
import json
import pandas as pd

if __name__ == '__main__':
    # input what path to save the data!
    ABSOLUTE_PATH_TO_SAVE = 'Z:/Lab/Cantilever/Measurements/20160330_TransmissionvsTemp/'
    if not ABSOLUTE_PATH_TO_SAVE:
        message = 'PLEASE SET IT!'
        raise AttributeError(message)

    # Setting up the Spectrum Analyzer
    spec_anal = SpectrumAnalyzer()
    spec_anal.mode = 'TrackingGenerator'
    spec_anal.output_on = True
    spec_anal.output_power = 0.0  #dBm
    spec_anal.start_frequency = 1e6  # arbitrary, can't set to 0 because of spectrum analyzer limitations
    spec_anal.end_frequency = 3e9

    init_time = time.strftime('%Y_%m_%d_%H_%M_%S')

    data = {'time': [], 'stage1_temp': [], 'stage2_temp': [], 'platform_temp': [], 'trace': []}
    with open(ABSOLUTE_PATH_TO_SAVE + init_time + '_spectrum_vs_temp' + '.json', 'a') as fp:
        json.dump(data, fp)

    while True:
        with open(ABSOLUTE_PATH_TO_SAVE + init_time + '_spectrum_vs_temp' + '.json', 'r+') as fp:
            data = json.load(fp)
            cur_time = time.strftime('%Y_%m_%d_%H_%M_%S')
            data['time'].append(cur_time)
            temps = TemperatureData.get_current_temps()
            data['stage1_temp'].append(float(temps[1]))
            data['stage2_temp'].append(float(temps[2]))
            data['platform_temp'].append(float(temps[0]))
            data['trace'].append(spec_anal.trace)
            print('wrote to file!')

        with open(ABSOLUTE_PATH_TO_SAVE + init_time + '_spectrum_vs_temp' + '.json', 'w+') as fp:
            fp.write(json.dumps(data))

        #trace.to_csv(ABSOLUTE_PATH_TO_SAVE + 'trace' + cur_time + '.csv', index = False, header = None)
        #print('saved trace!')
        time.sleep(60)  #since the spectrum analyzer takes a full second =)
