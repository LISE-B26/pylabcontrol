if __name__ == '__main__':
    zi = ZIHF2(1, .5)
    zi.sweep(1e6, 50e6, 100, 10, xScale = 0)
    zi.plot()