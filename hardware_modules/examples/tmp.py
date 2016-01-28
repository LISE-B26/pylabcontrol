fun_name = "test"

exec("""def {:s}(value):
    return value+2""".format(fun_name))

print(test(4))