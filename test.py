import numpy as np

num_daq_reads = 3
reps = 10

signal = [0]
norms = np.repeat([1], (num_daq_reads - 1))
count_data = np.repeat([np.append(signal, norms)], reps, axis=0)
print(np.append(signal, norms))
print(count_data)
print(count_data[5] + [1, 1, 1])
