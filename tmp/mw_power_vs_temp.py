from src.instruments.spectrum_analyzer import SpectrumAnalyzer
from src.instruments import MicrowaveGenerator
from legacy_src.old_hardware_modules.Cryostation import TemperatureData
import time
import json
import pandas as pd

if __name__ == '__main__':
    # input what path to save the data!
    ABSOLUTE_PATH_TO_SAVE = 'Z:/Lab/Cantilever/Measurements/20160405_CPW_power_vs_temp/'

    # Setting up the Spectrum Analyzer
    spec_anal = SpectrumAnalyzer()
    spec_anal.start_frequency = 2.7e9  # arbitrary, can't set to 0 because of spectrum analyzer limitations
    spec_anal.end_frequency = 3e9

    # Setting up the microwave generator
    mw_generator = MicrowaveGenerator()
    mw_generator.FREQ = 2.85e9
    init_time = time.strftime('%Y_%m_%d_%H_%M_%S')

    init_time = time.strftime('%Y_%m_%d_%H_%M_%S')

    data = {'time': [], 'stage1_temp': [], 'stage2_temp': [], 'platform_temp': [], 'trace': []}
    with open(ABSOLUTE_PATH_TO_SAVE + init_time + '_power_vs_temp' + '.json', 'a') as fp:
        json.dump(data, fp)

    for power in range(-45, -12, 2):
        with open(ABSOLUTE_PATH_TO_SAVE + init_time + '_power_vs_temp' + '.json', 'r+') as fp:
            mw_generator.AMPR = power
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
        time.sleep(6)  #since the spectrum analyzer takes a full second =)
