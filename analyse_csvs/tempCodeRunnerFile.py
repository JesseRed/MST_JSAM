    seed(1)
    # prepare data
    data1 = 10 * randn(10000) + 60
    data2 = 10 * randn(10000) + 55
    # calculate cohen's d
    print(type(data1))
    d = cohend(data1, data2)
    print('Cohens d: %.3f' % d)