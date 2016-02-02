__author__ = 'Experiment'


import hardware_modules.ZiControl as zi
'''Test script to check functionality of ZiControl.py script:
set values here and check in the ZI software if the rigth changes where applied
'''

amplitude = 1.2
zi_parameter = {
    'amplitude' : amplitude,
    'offset' : 3.0,
    'freq' : 1e5,
    'ACCoupling' : 0,
    'inChannel' : 0,
    'outChannel' : 0,
    'auxChannel': 0,
    'add' : 1,
    'range' : 1.0 if amplitude <= 1.0 else 10
}


amplitude = 0.05
zi_parameter = {
    'amplitude' : amplitude,
    'offset' : 3.0,
    'freq' : 1e5,
    'ACCoupling' : 0,
    'inChannel' : 0,
    'outChannel' : 0,
    'auxChannel': 0,
    'add' : 1,
    'range' : 10**int(np.ceil(np.log10(amplitude)))
}


zi_hf2 = zi.ZIHF2(zi_parameter['amplitude'],
                  zi_parameter['offset'],
                  zi_parameter['freq'],
                  zi_parameter['ACCoupling'],
                  zi_parameter['inChannel'],
                  zi_parameter['outChannel'],
                  zi_parameter['auxChannel'],
                  zi_parameter['add'],
                  zi_parameter['range']
                 )