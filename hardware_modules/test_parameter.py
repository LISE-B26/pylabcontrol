from unittest import TestCase
from instruments import Parameter

class TestParameter(TestCase):

    # initiate Paremater in all possible ways
    p1 = Parameter('param', 0.0)
    p2 = Parameter('param', 0, int, 'test int')
    p3 = Parameter('param', 0.0, (int, float), 'test tupple')
    p4 = Parameter('param', 0.0, [0.0, 0.1], 'test list')
    print('passed single parameter test')

    p_nested = Parameter('param nested', p1, None, 'test list')
    p_nested = Parameter('param nested', p4, [p1,p4], 'test list')
    print('passed nested parameter test')

    p_dict = Parameter({'param dict': 0 })
    print(p_dict)
    print('passed dictionary test')
    p_dict_nested = Parameter({'param dict': {'sub param dict': 1 } })
    print(p_dict_nested.name, p_dict_nested.value, p_dict_nested.info)
print('passed nested dictionary test')
