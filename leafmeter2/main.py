import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import pyqtSlot as slot
import pyqtgraph as pg
import matplotlib.pyplot as plt
from pyqtgraph.graphicsItems.ROI import ROI

#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(imageAxisOrder='row-major')

def hex2pen(x):
    return pg.mkPen(x)

BLUE = hex2pen("#1f77b4")
GREEN = hex2pen("#2ca02c")
ORANGE = hex2pen('#ff7f0e')
RED = hex2pen('#d62728')

Design, _ = uic.loadUiType('design.ui')

_L, _a, _b = 0, 1, 2

class TestROI(ROI):
    def __init__(self, pos, size, **args):
        ROI.__init__(self, pos, size, **args)
        self.addTranslateHandle([0.5, 0.5])
        self.addScaleHandle([1, 1], [0, 0])
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 0.5], [0, 0.5])
        self.addScaleHandle([0.5, 1], [0.5, 0])
        self.addScaleHandle([0, 0.5], [1, 0.5])
        self.addScaleHandle([0.5, 0], [0.5, 1])
        self.addScaleHandle([1, 0], [0, 1])
        self.addScaleHandle([0, 1], [1, 0])

class ExampleApp(QtWidgets.QMainWindow, Design):
    def updateRoi(self, roi):
        if roi is None:
            return
        #print(roi.pos(), roi.size(), roi.getAffineSliceParams(self.im1.image, self.im1))
        
        a0, b0 = roi.pos()
        a1, b1 = roi.pos() + roi.size()
        #mask = (lab[:,:,_L] > ref[_L]-5) & (lab[:,:,_L] < ref[_L]+5) & \
        mask = (self.lab[:,:,_a] >= a0) & (self.lab[:,:,_a] <= a1) & \
            (self.lab[:,:,_b] >= b0) & (self.lab[:,:,_b] <= b1)
        
        rgbm = self.rgb.copy()
        rgbm[~mask] = [0,0,255]
        #lastRoi = roi
        #arr1 = roi.getArrayRegion(im1.image, img=im1)
        self.im3.setImage(rgbm)
        w, h, c = self.lab.shape
        self.percent.setText('%.2f%%' % (len(np.nonzero(mask)[0]) / (w*h) * 100))
    
#    def updateRoiPlot(self, roi, a=None, b=None):
#        if a is None:
#            a = roi.getArrayRegion(self.lab[:,:,1], img=self.im1)
#            b = roi.getArrayRegion(self.lab[:,:,2], img=self.im1)
#        if a is not None:
#            roi.curve.setData({'x': a.flatten(), 'y': b.flatten()})#data.mean(axis=1))

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        w = self.canvas

        ## create GUI
        Q = 100
        self.rgb = plt.imread('7.jpg')[1000-Q:1000+Q,1500-Q:1500+Q,:]
        self.lab = np.load('7.npz')['arr_0'][1000-Q:1000+Q,1500-Q:1500+Q,:]

        arr = self.lab[:,:,0]

        # This is the main graphics widget
        #w = pg.GraphicsLayoutWidget(show=True, size=(800,800), border=True)

        # Top-left scene in the graphics widget
        v = w.addViewBox(0,0)
        v.invertY(True)  ## Images usually have their Y-axis pointing downward
        v.setAspectLocked(True)
        self.im1 = pg.ImageItem(self.rgb)   # Create image widget, add to scene and set position 
        v.addItem(self.im1)
        v.setRange(QtCore.QRectF(0, 0, 200, 120))

        # Top-right scene in the graphics widget
        v2 = w.addViewBox(0,1)
        self.im3 = pg.ImageItem()
        v2.addItem(self.im3)
        v2.setRange(QtCore.QRectF(0, 0, 60, 60))
        v2.invertY(True)
        v2.setAspectLocked(True)
        self.im3.setZValue(10)

        # Bottom plot in the main graphics widget
        pi1 = w.addPlot(1,0, colspan=2)
        pi1.setXRange(-100, 100, padding=0)
        pi1.setYRange(-100, 100, padding=0)
        pi1.showGrid(x = True, y = True, alpha = 0.3)

        # Create ROIs
        #lastRoi = None

        rois = [
            TestROI(
                [0, 0],
                [20, 20],
                maxBounds=QtCore.QRectF(-100, -100, 230, 230),
                pen=(0, 9),
            )
        ]

        # Add each ROI to the scene and link its data to a plot curve with the same color
        for r in rois:
            pi1.addItem(r)
            c = pi1.plot(x=[1,2,3], y=[1,4,9], pen=(0,0,0), symbol='o', symbolSize=5)
            r.curve = c
            r.sigRegionChanged.connect(self.updateRoi)

        a = self.lab[:,:,1]
        b = self.lab[:,:,2]
        rois[0].curve.setData({'x': a.flatten(), 'y': b.flatten()})#data.mean(axis=1))
        self.actionOpen.triggered.connect(self.open_file)
        
#        self.curve = self.canvas.plot([1,4,9], symbol='o', symbolSize=5, pen=BLUE)
#  ‘o’ circle (default) * ‘s’ square * ‘t’ triangle * ‘d’ diamond * ‘+’ plus

    @slot()
    def open_file(self):
        imagePath, _ = QtWidgets.QFileDialog.getOpenFileName()
        self.jpg_filename.setText(imagePath)

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))   # Более современная тема оформления
    app.setPalette(QtWidgets.QApplication.style().standardPalette())  # Берём цвета из темы оформления
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
