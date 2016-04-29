import pandas as pd
import os
import glob

path = 'Z:\\Lab\\Cantilever\\Measurements\\160414_MW_transmission_vs_Power_at_cold_temperature\\'

data = {}

data_files = os.listdir(path + '\data')
data_names = set([f.split('.')[1] for f in data_files])
time_tags = set(['_'.join(f.split('_')[0:3]) for f in data_files])

for time_tag in time_tags:
    sub_data = {}
    for data_name in data_names:
        file_path = "{:s}\\data\\{:s}*.{:s}".format(path, time_tag, data_name)
        df = pd.read_csv(glob.glob(file_path)[0], index_col = False, header=-1)
        # separates the case of reading a list of values vs reading an array
        if len(df.values[0]) == 1:
            sub_data.update({data_name: df.values.flatten().tolist()})
        else:
            sub_data.update({data_name: df.values.tolist()})
    data.update({time_tag: sub_data})

time_tag_in = None
if time_tag_in != None:
    # if user specifies a time_tag we only return that specific data set
    data = data[time_tag_in]
elif len(data) == 1:
    # if there is only one data_set, we strip of the time_tag level
    data = data[data.keys()[0]]

print(len(data['spectrum']))
