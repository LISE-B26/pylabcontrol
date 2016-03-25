if __name__ == '__main__':
    parameter = {"par2":3,"par1": 1, "dict": {'proportional': 1241412, 'integral':0},}
    def fun(xx, par1, par2, dict):
        print('xx: ', xx)
        print('paramter1: ', par1)
        print('paramter2: ', par2)
        print('dict: ', dict['proportional'])


    fun('ada', **parameter)

#
#
# data = {'school':'DAV', 'standard': '7', 'name': 'abc', 'city': 'delhi'}
# my_function(*data)
#
# my_function(*data):
#     schoolname  = school
#     cityname = city
#     standard = standard
#     studentname = name