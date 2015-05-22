import pandas as pd
import time


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