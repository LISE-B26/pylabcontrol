import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.old_functions import Focusing as F

if __name__ == '__main__':
    path = 'Z:\\Lab\\Cantilever\\Measurements\\20150804_DistanceMeas\\2nd set\\*_focus.csv'
    files = glob.glob(path)
    files.sort()

    gold_vals = list()
    gold_err = list()
    nv_vals = list()
    nv_err = list()

    for f in files:
        print(f)
        df = pd.read_csv(f, header = -1)
        voltages = df.values[0]
        stddev = df.values[1]
        (a,mean,sigma,c),_ = F.Focus.fit(voltages, stddev)
        fitdata = (F.Focus.gaussian(voltages, a, mean, sigma, c))
        #plt.plot(voltages, stddev, voltages, fitdata)
        #plt.show()
        if 'gold' in f:
            gold_vals.append(mean)
            gold_err.append(sigma)
        else:
            nv_vals.append(mean)
            nv_err.append(sigma)

    gold_err = map(lambda x: x**2, gold_err)
    nv_err = map(lambda x: x**2, nv_err)

    print('gold: ' + str(np.mean(gold_vals)) + ' +- ' + str((np.sum(gold_err)**(.5))/len(gold_vals)))
    print('nv: ' + str(np.mean(nv_vals)) + ' +- ' + str((np.sum(nv_err)**(.5))/len(nv_vals)))

    plt.hist(gold_vals,4, label = 'Gold')
    plt.hist(nv_vals,4, label = 'NVs')
    plt.xlabel('Distance (um)')
    plt.ylabel('Number of Scans')
    plt.legend()
    plt.show()