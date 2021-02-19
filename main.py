# -*- coding: utf-8 -*-
## Add path to library (just for examples; you do not need this)
#import initExample

from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt

pg.setConfigOptions(imageAxisOrder='row-major')

## create GUI
app = QtGui.QApplication([])

Q = 100
rgb = plt.imread('7.jpg')[1000-Q:1000+Q,1500-Q:1500+Q,:]
lab = np.load('7.npz')['arr_0'][1000-Q:1000+Q,1500-Q:1500+Q,:]

arr = lab[:,:,0]

w = pg.GraphicsLayoutWidget(show=True, size=(800,800), border=True)
v = w.addViewBox(0,0)
v.invertY(True)  ## Images usually have their Y-axis pointing downward
v.setAspectLocked(True)

## Create image items, add to scene and set position 
im1 = pg.ImageItem(rgb)
v.addItem(im1)
v.setRange(QtCore.QRectF(0, 0, 200, 120))
#im1.scale(0.8, 0.5)

im3 = pg.ImageItem()
v2 = w.addViewBox(0,1)
v2.addItem(im3)
v2.setRange(QtCore.QRectF(0, 0, 60, 60))
v2.invertY(True)
v2.setAspectLocked(True)
im3.setZValue(10)

## create the plot
pi1 = w.addPlot(1,0, colspan=2)
pi1.setXRange(-100, 100, padding=0)
pi1.setYRange(-100, 100, padding=0)
pi1.showGrid(x = True, y = True, alpha = 0.3)

lastRoi = None

def updateRoi(roi):
    global im1, im3, arr, lastRoi
    if roi is None:
        return
    lastRoi = roi
    arr1 = roi.getArrayRegion(im1.image, img=im1)
    a = roi.getArrayRegion(lab[:,:,1], img=im1)
    b = roi.getArrayRegion(lab[:,:,2], img=im1)
    im3.setImage(arr1)
    updateRoiPlot(roi, a, b)
  
def updateRoiPlot(roi, a=None, b=None):
    if a is None:
        a = roi.getArrayRegion(lab[:,:,1], img=im1)
        b = roi.getArrayRegion(lab[:,:,2], img=im1)
    if a is not None:
        roi.curve.setData({'x': a.flatten(), 'y': b.flatten()})#data.mean(axis=1))


## Create a variety of different ROI types
rois = []
rois.append(pg.TestROI([0,  0], [20, 20], maxBounds=QtCore.QRectF(-10, -10, 230, 140), pen=(0,9)))

## Add each ROI to the scene and link its data to a plot curve with the same color
for r in rois:
    v.addItem(r)
    c = pi1.plot(x=[1,2,3], y=[1,4,9], pen=(0,0,0), symbol='o', symbolSize=5)
    r.curve = c
    r.sigRegionChanged.connect(updateRoi)

def updateImage():
    global im1, arr, lastRoi
    updateRoi(lastRoi)
    for r in rois:
        updateRoiPlot(r)
    
## Rapidly update one of the images with random noise    
t = QtCore.QTimer()
t.timeout.connect(updateImage)
t.start(50)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
