__author__ = 'Experiment'

'''
    functions related to ducktype test of variables
'''
import json as json

def is_autofocus_param(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False

    assert 'zo' in json_object.keys()
    assert 'dz' in json_object.keys()
    assert 'zPts' in json_object.keys()
    assert 'xyPts' in json_object.keys()

    return True


def is_ESR_param(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False

    assert 'RF_Power' in json_object.keys()
    assert 'ESR_avg' in json_object.keys()
    assert 'RF_Min' in json_object.keys()
    assert 'RF_Max' in json_object.keys()
    assert 'RF_N_Points' in json_object.keys()
    assert 'ESR_path' in json_object.keys()
    assert 'ESR_tag' in json_object.keys()
    assert 'ESR_integration_time' in json_object.keys()


    return True