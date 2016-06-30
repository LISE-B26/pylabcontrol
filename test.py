import itertools

a = [1, 2, 3, 4, 5, 6]

multiple = 6
for start in range(multiple):
    print sum(itertools.islice(a, start, None, multiple))
