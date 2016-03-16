import glob

import numpy as np
import pandas as pd
import scipy.signal


def analyze_dist():
    path = 'Z:\\Lab\\Cantilever\Measurements\\20151118_dist_d7_to_chip\\*.csv'
    files = glob.glob(path)
    files.sort()
    data_list = list()
    for f in files:
        data_list.append(pd.read_csv(f, header=-1))
    print('finished reading')

    for i in xrange(0,data_list.__len__()):
        max_index = scipy.signal.argrelmax(np.array(data_list[i])[2,1:], order=10)
        max_val = np.max(np.array(data_list[i])[2,1:])
        del_mat = []
        index = 0
        for num in max_index[0]:
            if np.array(data_list[i])[2,num]*10 < max_val:
                del_mat.append(index)
            index += 1
        max_index = np.delete(max_index[0],del_mat)
        print np.array(data_list[i])[1,max_index]
        print np.array(data_list[i])[2,max_index]


analyze_dist()