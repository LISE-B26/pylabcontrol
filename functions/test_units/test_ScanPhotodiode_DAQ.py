import functions.ScanPhotodiode_DAQ as SP

# Test code to run scan and display image
newScan = SP.DaqOut(-.4, .4, 401, -.4, .4, 401, .002)
print newScan.scan_time()
#newScan.scan()
#newScan.dispImage()