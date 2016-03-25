__author__ = 'Experiment'

'''
    old_functions related to ducktype test of variables
'''
import json as json

def dict_difference(dict1, dict2):
    '''
    checks if two dictionaries have the same keys
    if they have the same keys but different values it returns a dictionary of the values that are different
    with values corresponding to dict1
    returns:
        identical - booean, true is the dictionaries are identical
        dict_diff - dictionary containing the entries that are different
    '''
    identical = True
    dict_diff = {}
    if sorted(dict1.keys()) == sorted(dict2.keys()):

        for key, value in dict1.iteritems():
            if type(value) is dict:
                print('element is dict')
                identical_sub, diff_keys_sub = comp_dict(dict1[key], dict2[key])
                if identical_sub is False:
                    identical = False
                    dict_diff.update({key:diff_keys_sub})

            else:
                if dict1[key] is not dict2[key]:
                    identical = False
                    print(dict1[key], dict2[key])
                    dict_diff.update({key:dict1[key]})
    else:
        print('keys don\'t match')
        identical = False

    return identical, dict_diff


def is_autofocus_param(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False

    assert 'zo' in json_object.keys()
    assert 'dz' in json_object.keys()
    assert 'zPts' in json_object.keys()
    assert 'xyPts' in json_object.keys()
    # assert 'axis' in json_object.keys()

    return True

def is_counter_param(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False

    assert 'sample_rate' in json_object.keys()
    assert 'time_per_pt' in json_object.keys()

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