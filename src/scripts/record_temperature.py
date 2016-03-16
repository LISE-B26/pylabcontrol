__author__ = 'Experiment'

import time

import hardware_modules.Cryostation as cryo
import hardware_modules.GaugeController as GC
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import src.hardware_modules.TempController as TC


def record_temp():
    cryostat = cryo.Cryostation('10.243.34.189', 7773)
    tc = TC.Lakeshore335()
    gc = GC.AGC100()
    temperature_data = pd.DataFrame(columns=['time', 'platform_temp',
                                             'sample_temp', 'stage1_temp', 'stage2_temp', 'surface_temp', 'pressure'])

    while(True):
        temperature_data = temperature_data.append(pd.DataFrame([[time.strftime("%H:%M:%S"),
                                cryostat.get_platform_temp(),
                                cryostat.get_sample_temp(),
                                cryostat.get_stage_one_temp(),
                                cryostat.get_stage_two_temp(),
                                tc.get_temp(),
                                gc.getPressure()]],
                                columns=['time', 'platform_temp',
                                         'sample_temp', 'stage1_temp', 'stage2_temp', 'surface_temp', 'pressure'],
                                ), ignore_index=True)

        temperature_data.to_csv('C:/Users/Experiment/Desktop/20150915_Cooldown/temperature_data_shield_5.csv', index=False)
        time.sleep(15)

def plot_temp():
    df = pd.read_csv('C:/Users/Experiment/Desktop/20150915_Cooldown/temperature_data_shield_3_warmup.csv')
    data = df.values
    cryo = data[:,2]
    sample = data[:,5]
    time = np.linspace(0,15*len(data),num=len(data))
    plt.plot(time,cryo, time, sample)
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (K)')
    plt.show()

record_temp()