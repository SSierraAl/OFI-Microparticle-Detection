from random import randint
import numpy as np
import pyqtgraph as pg




def InitFluigent_Sensor(self):

    self.graphWidget = pg.PlotWidget()
    self.x = list(range(10000))  # 100 time points
    self.y = [randint(0,100) for _ in range(10000)]  # 100 data points
    self.graphWidget.setBackground('w')
    pen = pg.mkPen(color=(250, 100, 100))
    self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

    self.graphWidget2 = pg.PlotWidget()
    self.x2 = list(range(10000))  # 100 time points
    self.y2 = [randint(0,100) for _ in range(10000)]  # 100 data points
    self.graphWidget2.setBackground('w')
    pen2 = pg.mkPen(color=(250, 100, 100))
    self.data_line2 =  self.graphWidget2.plot(self.x2, self.y2, pen=pen2)



    self.graphWidget3=pg.GraphicsLayoutWidget()
    self.graphWidget3.setBackground('w')
    self.p1 = self.graphWidget3.addPlot(row=0,col=0)
    self.p2 = self.graphWidget3.addPlot(row=1, col=0)
    self.p3 = self.graphWidget3.addPlot(row=2, col=0)
    self.p4 = self.graphWidget3.addPlot(row=3, col=0)
    #self.p1.showAxis('right')
    self.p2.showAxis('right')
    self.p2.hideAxis('left')
    
    #self.p1.scene().addItem(self.p2)
    #self.p1.getAxis('right').linkToView(self.p2)
    #self.p2.setXLink(self.p1)
    
    #self.p2.getAxis('right').setLabel('axis2', color='#0000ff')




    self.x3 = list(range(10000))  # 100 time points

    self.y3 = [randint(0,100) for _ in range(10000)]  # 100 data points
    self.y4 = [randint(0,50) for _ in range(10000)]
    pen3 = pg.mkPen(color=(250, 100, 100))
    pen4 = pg.mkPen(color=(100, 100, 100))

    self.data_line3 =  self.p1.plot(self.x3, self.y3, pen=pen3)
    self.data_line4 =  self.p2.plot(self.x3, self.y4, pen=pen4)
    self.data_line5 =  self.p3.plot(self.x3, self.y3, pen=pen3)
    self.data_line6 =  self.p4.plot(self.x3, self.y4, pen=pen4)



    self.ui.load_pages.verticalLayout_9.addWidget(self.graphWidget)
    self.ui.load_pages.verticalLayout_7.addWidget(self.graphWidget2)
    self.ui.load_pages.verticalLayout_8.addWidget(self.graphWidget3)







