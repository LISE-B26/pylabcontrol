import pandas as pd
import time
import json as json
'''
    functions related reading and writing data
'''


def save_esr_data(esr_data, filename):
    '''
    not implemented yet, saves esr
    :param esr_data:
    :param filename:
    :return:
    '''

def load_esr_data(filename):
    '''
    not implemented yet, loads esr
    :param esr_data:
    :param filename:
    :return: esr_data
    '''


def save_image_and_data(fig, array, dirpath, tag, columns = None):
    df = pd.DataFrame(array, columns = columns)
    if(columns == None):
        header = False
    else:
        header = True
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    filename = '\\' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second  +'-' + str(tag)
    filepathCSV = dirpath + filename + '.csv'
    filepathJPG = dirpath + filename + '.jpg'
    df.to_csv(filepathCSV, index = False, header=header)
    fig.savefig(str(filepathJPG), format = 'jpg')

def load_json(filename = None):

    if filename is None:
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Z://Lab//Cantilever//Measurements//')
    json_dict  = {}
    if not filename == '':
        print('loading {:s}'.format(filename))
        with open(filename, 'r') as infile:
            json_dict = json.load(infile)
    else:
        print('{:s} not found'.format(filename))

    return json_dict

def save_json(json_dict, filename = None):

    if filename is None:
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Z://Lab//Cantilever//Measurements//')

    print json_dict
    with open(filename, 'w') as outfile:
        tmp = json.dump(json_dict, outfile, indent=4)
