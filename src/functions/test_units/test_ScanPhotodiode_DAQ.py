from src import functions as SP

if __name__ == '__main__':
    # Test code to run scan and display image
    newScan = SP.DaqOut(-.4, .4, 401, -.4, .4, 401, .002)
    print newScan.scan_time()
    #newScan.scan()
    #newScan.dispImage()