__author__ = 'Experiment'


# no finished at all


scanner = GalvoScan.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
imageData = scanner.scan(queue = queue)
setDaqPt(0,0)