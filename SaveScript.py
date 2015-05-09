# B26 Lab Code
# Last Update: 4/21/15

import os, inspect
import win32file
import pywintypes

# This function saves a copy of the current function to the given path
# savePath: the path in which the copy is saved
def saveScript(savePath):
    try:
        curframe = inspect.currentframe()
        outframes = inspect.getouterframes(curframe)
        origPath = outframes[1][1]
        win32file.CopyFile (origPath, savePath, 1)
        if not os.path.isfile (savePath): raise IOError('Saving Script Failed')
    except pywintypes.error:
        print("Attempted to save script over existing file. Choose another path.")