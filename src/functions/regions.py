__author__ = 'Experiment'


def roi_to_min_max(roi):
    '''
        returns min and max values for RoI
    '''
    xMin, xMax = roi['xo'] - roi['dx']/2., roi['xo'] + roi['dx']/2.
    yMin, yMax = roi['yo'] - roi['dy']/2., roi['yo'] + roi['dy']/2.
    return xMin, xMax, yMin, yMax


def min_max_to_roi(xMin, xMax, yMin, yMax):
    '''
        returns  RoI from min and max values
    '''

    roi = {
        "dx": xMax - xMin,
        "dy": yMax - yMin,
        "xo": (xMax + xMin)/2,
        "yo": (yMax + yMin)/2
    }

    return roi


def assert_is_roi(roi):
    '''
        check if dictionary qualifies as RoI
    '''
    assert 'dx' in roi
    assert 'dy' in roi
    assert 'xo' in roi
    assert 'yo' in roi
    assert 'xPts' in roi
    assert 'yPts' in roi

    return True

def roi_crop(roi):
    '''
        if roi extend beyond bound +-0.5 crop it
    '''

    assert_is_roi

    xMin, xMax, yMin, yMax = roi_to_min_max(roi)

    if xMin < -0.5: roi.update({'dx' : roi['xo'] +0.5})
    if xMax > 0.5: roi.update({'dx' :  0.5 - roi['xo']})
    if yMin < -0.5: roi.update({'dy' : roi['yo'] +0.5})
    if yMax > 0.5: roi.update({'dy' : 0.5 - roi['yo']})



####################################################################################
####################################################################################
# testing stuff
####################################################################################
roi = {
    "dx": 0.1,
    "dy": 0.1,
    "xPts": 20,
    "xo": -0.45,
    "yPts": 20,
    "yo": 0.0
}
#
# print roi
# roi_crop(roi)
# print roi

print roi_to_min_max(roi)
