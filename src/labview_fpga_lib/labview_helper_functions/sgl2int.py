"""
Created on January 26th

@author: Jan Gieseler

A collection of function to map floating point numbers to integers (32 bit) and back
needed for sending floating point numbers to Labview FPGA, since the c-compiled FPGA code doesn't accept floats

test unit: test_sgl2int.py

"""


import numpy as np
import math as math


# =========== definitions =======================

# calculate the boolean array for the mantissa
def mantissa_2_bool(x, boolean_array = []):
    '''
    :param x: matissa that is converted into a boolean array and appended to boolean_array
    :param boolean_array: append the boolean are from x to this array
    :return:
    '''
    for i in range(23):
        x_bin = 2.0**(-(i+1))
        if x_bin <= (x-1):
            x -= x_bin
            boolean_array.append(True)
        else:
            boolean_array.append(False)
        # print(i, x, x_bin, x_bin <= (x-1))

    # return(boolean_array)

def int_2_bool(x, boolean_array = [], inttype = 'I8'):
    '''
    converts the integer x into the equivalent boolean array of length inttype
    :param x: integer to be converted
    :param boolean_array: array to which converted integer array is appended
    :param inttype: type of integer (determines the length of the boolean array)
    :return:
    '''
    inttypes = {'U8':7,'U16':15,'U32':31, 'I8':7,'I16':15,'I32':31}
    if inttype in {'I8', 'I16', 'I32'}:
        x += 2.0**(inttypes[inttype]+1)

    for i in range(inttypes[inttype],-1,-1):
        x_bin = 2.0**(i)
        # print(i, x_bin, x)
        if x_bin <= x:
            x -= x_bin
            boolean_array.append(True)
        else:
            boolean_array.append(False)

    # return(boolean_array)

def exponent_to_bool(x, boolean_array):
    '''

    :param x: exponent that is converted into a boolean array and appended to boolean_array
    :param boolean_array: append the boolean are from x to this array
    :return:
    '''
    int_2_bool(x+127, boolean_array, 'U8')

def bool_2_int(boolean_array):
    return int(np.sum(np.array(boolean_array) * 2.0**np.arange(len(boolean_array))))

def SGL_to_U32(x):
    '''
    converts a floating point number (sgl) into the equivalent 32bit integer
    :param x: floating point number, i.e. sgl
    :return: 32 bit integer
    '''
    (mantissa, exponent) = math.frexp(x)
    (sign, mantissa, exponent) = (np.sign(mantissa),abs(mantissa*2), exponent-1) # use same definitions as in Labview

    boolean_array = [sign<0]
    exponent_to_bool(exponent, boolean_array)
    mantissa_2_bool(mantissa, boolean_array)

    return( bool_2_int(boolean_array) )

def U32_to_SGL(x):
    '''
    converts a 32bit integer into the equivalent floating point number (sgl)
    :param x: 32 bit integer
    :return: floating point number, i.e. sgl
    '''
    boolean_array = []
    int_2_bool(x, boolean_array, 'U32')
    boolean_array = boolean_array[::-1]
    sign = boolean_array[0]
    exponent_bool = boolean_array[1:9]
    mantissa_bool = boolean_array[9:]

    exponent = bool_2_int(exponent_bool[::-1])-127

    mantissa = np.sum(2.0**( -(np.arange(len(mantissa_bool))+1) ) * mantissa_bool) + 1

    SGL = -1 if sign else 1
    SGL *= mantissa * 2.0**exponent
    return SGL
