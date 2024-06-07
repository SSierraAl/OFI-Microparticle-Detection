

from Frequency_Func import *
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel,QVBoxLayout,QGraphicsView
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor

import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode

def Set_Scanning_Tab(self):

    class ColorGrid(QWidget):
        def __init__(self, g_W, g_H, cell_size):
            super().__init__()
            self.g_W = g_W
            self.g_H = g_H
            self.cell_size = cell_size

            #Matrix to export CSV data
            self.CSV_Moments_M0_Matrix=np.zeros((self.g_W,self.g_H))
            self.CSV_Moments_M1_Matrix=np.zeros((self.g_W,self.g_H))
            self.CSV_Moments_Matrix=np.zeros((self.g_W,self.g_H))

            # Configurar la vista de gráficos
            self.graphicsView = pg.GraphicsView()
            self.graphicsView.setBackgroundBrush(QColor('white'))
            self.graphicsLayout = pg.GraphicsLayout()
            self.graphicsView.setCentralItem(self.graphicsLayout)

            # Crear PlotItem y agregarlo al GraphicsLayout
            self.plotItem = self.graphicsLayout.addPlot()
            self.plotItem.showGrid(x=True, y=True)
            self.plotItem.setRange(xRange=(0, self.g_W), yRange=(0, self.g_H), padding=0)
            # Crear el ImageItem y agregarlo al PlotItem
            self.imageItem = pg.ImageItem()
            self.plotItem.addItem(self.imageItem)
            self.plotItem.getViewBox().setBackgroundColor('w')
            self.gridArray = np.ones((self.g_H, self.g_W, 3), dtype=np.uint8)*255

            # Configurar el diseño
            layout = QVBoxLayout(self)
            layout.addWidget(self.graphicsView)

            self.timer_Calib_Scan = QTimer(self)
            self.timer_Calib_Scan.setInterval(1000)  # Intervalo en milisegundos
            self.timer_Calib_Scan.timeout.connect(self.updatePixel)

            # Variables para recorrer los píxeles
            self.current_row = 0
            self.current_col = 0


        def updatePixel(self):

            # Cambiar el color del píxel actual
            self.gridArray[self.current_row, self.current_col] = [255, 0, 0]  # Rojo
            # Actualizar la imagen
            self.imageItem.setImage(self.gridArray, autoLevels=False)
            # Moverse al siguiente píxel
            self.current_col += 1
            if self.current_col >= self.g_W:
                self.current_col = 0
                self.current_row += 1
                if self.current_row >= self.g_H:
                    self.current_row = 0


        def changeCellColor(self, row, col, color):
            self.gridArray[row, col] = color
            self.imageItem.setImage(self.gridArray, autoLevels=False)



        def Start_Grid_Scan(self):
            self.timer_Calib_Scan.start()

        def Stop_Grid_Scan(self):
            self.timer_Calib_Scan.stop()

        def update_white(self):
            self.gridArray = np.zeros((self.g_H, self.g_W, 3), dtype=np.uint8)*255
            self.imageItem.setImage(self.gridArray, autoLevels=False)

        ### Export CSV functions
        def updateCSV(self, row, col, Moment, M0, M1):
            self.CSV_Moments_Matrix[row, col] = Moment
            self.CSV_Moments_M0_Matrix[row, col] = M0
            self.CSV_Moments_M1_Matrix[row, col] = M1

        def exportar_Matrix_CSV(self):
            df = pd.DataFrame(self.CSV_Moments_Matrix)
            df.to_csv('Scanning_Moments_CSV.csv', index=True)
            df = pd.DataFrame(self.CSV_Moments_M0_Matrix)
            df.to_csv('Scanning_Moments_M0_CSV.csv', index=True)
            df = pd.DataFrame(self.CSV_Moments_M1_Matrix)
            df.to_csv('Scanning_Moments_M1_CSV.csv', index=True)

    ################################################
    ################################################

    def start_refrehs_scan():
        self.color_grid_widget.Start_Grid_Scan()

    def stop_refrehs_scan():
        self.color_grid_widget.Stop_Grid_Scan()

    def reset_refrehs_scan():
        self.color_grid_widget.update_white()
        self.color_grid_widget.Stop_Grid_Scan()
        if self.color_grid_widget is not None:
            self.ui.load_pages.Layout_table_Scan.removeWidget(self.color_grid_widget)
 

    def Update_Scan_Param():
            width_g=int(self.ui.load_pages.lineEdit_Grid_Wsize.text())
            height_g=int(self.ui.load_pages.lineEdit_Grid_Hsize.text())
            cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text())
            self.color_grid_widget = ColorGrid(width_g,height_g,cell_size)
            self.ui.load_pages.Layout_table_Scan.addWidget(self.color_grid_widget)



    #Button connections
    self.ui.load_pages.Calib_Start_Scan_but.clicked.connect(start_refrehs_scan)
    self.ui.load_pages.Calib_Stop_Scan_but.clicked.connect(stop_refrehs_scan)
    self.ui.load_pages.Calib_Reset_Scan_but.clicked.connect(reset_refrehs_scan)
    self.ui.load_pages.update_param_scan_but.clicked.connect(Update_Scan_Param)




    ###################################################################
    ###################################################################
    #Zaber Functions
    ###################################################################
    ###################################################################

    self.Pos_Y1_Scan = float(self.ui.load_pages.lineEdit_y1_scan.text())
    self.Pos_Y2_Scan = float(self.ui.load_pages.lineEdit_y2_scan.text())
    self.speed = float(self.ui.load_pages.lineEdit_speed_ums.text()) * 1000 * 1.6381 / 1.9843
    self.time_timer_scan=0
    self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text()) 
    

    self.g_W=int(self.ui.load_pages.lineEdit_Grid_Wsize.text())
    self.g_W=int(self.g_W/self.cell_size)
    self.g_H=int(self.ui.load_pages.lineEdit_Grid_Hsize.text())
    self.g_H=int(self.g_H/self.cell_size)
    self.counter_Data_per_Pixel=0
    self.current_col=0
    self.current_row=0
    self.New_Color= [255,255,255]
    self.scanning_Finish=False

    #counter AVG DAQ data
    self.Counter_DAQ_samples=0
    self.PSD_Avg_Moment=0


    def Stop_z1():
        self.Pixel_Interval.stop()
        self.Pixel_Interval_X.stop()
        self.Adquisit_Timer.stop()
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            connection.generic_command(1, CommandCode.STOP, 1)


    def Stop_z2():

        #with Connection.open_serial_port(self.Zaber_COM) as connection:
        #    connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int(self.speed))

        self.Pixel_Interval.stop()
        self.Pixel_Interval_X.stop()
        self.Adquisit_Timer.stop()
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            connection.generic_command(3, CommandCode.STOP, 1)


    def move_to_position(Zab,position):
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            device_list[Zab].move_absolute(position, Units.LENGTH_MICROMETRES)

    def get_current_position(Zab):
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            act_pos=device_list[Zab].get_position(Units.LENGTH_MICROMETRES)
            return act_pos


    #########################################################
    #########################################################

    def start_continuous_movement():

        distance = abs(self.Pos_Y2_Scan - self.Pos_Y1_Scan)
        #self.time_to_travel = (distance / (self.speed * ((1.6381 / 1.9843))))*1000 # Convertir a milisegundos
        time_to_travel = (distance / float(self.ui.load_pages.lineEdit_speed_ums.text()))*1000 # Convertir a milisegundos
        self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text()) 
        self.time_timer_scan=((time_to_travel/(distance/self.cell_size)))

        with Connection.open_serial_port(self.Zaber_COM) as connection:
            connection.generic_command(1, CommandCode.MOVE_AT_CONSTANT_SPEED, int(self.speed))
        self.Pixel_Interval.setInterval(self.time_timer_scan)
        self.Pixel_Interval.start()

        self.Adquisit_Timer.start()

    def start_continuous_movement_X():
        distance = abs(self.Pos_X2_Scan - self.Pos_X1_Scan)
        #self.time_to_travel = (distance / (self.speed * ((1.6381 / 1.9843))))*1000 # Convertir a milisegundos
        time_to_travel = (distance / float(self.ui.load_pages.lineEdit_speed_ums.text()))*1000 # Convertir a milisegundos
        self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text()) 
        self.time_timer_scan=((time_to_travel/(distance/self.cell_size)))

        #print(time_to_travel)
        #print('aaaaaaaaaaaaaaa')
        #print(self.time_timer_scan)
        #ass

        

        with Connection.open_serial_port(self.Zaber_COM) as connection:
            connection.generic_command(3, CommandCode.MOVE_AT_CONSTANT_SPEED, int((((self.speed/1.55)/10)*1.6384/0.047625)    )    )#/0.047625)) #speed in um/s
        self.Pixel_Interval_X.setInterval(self.time_timer_scan)
        self.Pixel_Interval_X.start()

        self.Adquisit_Timer.start()
    #########################################################
    #########################################################

    def check_position_and_start_X(Zab, reference_Zab):
        if abs(get_current_position(Zab) - reference_Zab) < 10:
            start_continuous_movement_X()
        else:
            QTimer.singleShot(500, check_position_and_start_X(Zab,reference_Zab))


    def check_position_and_start(Zab, reference_Zab):
        if abs(get_current_position(Zab) - reference_Zab) < 10:
            start_continuous_movement()
        else:
            QTimer.singleShot(500, check_position_and_start(Zab,reference_Zab))


    #########################################################
    #########################################################

    def Scan_Continuos_Y():

        self.counter_Data_per_Pixel=0
        self.speed = float(self.ui.load_pages.lineEdit_speed_ums.text()) / ((1.6381 / 1.9843))
        self.Pos_Y1_Scan = float(self.ui.load_pages.lineEdit_y1_scan.text())
        self.Pos_Y2_Scan = float(self.ui.load_pages.lineEdit_y2_scan.text())
        self.Pos_X1_Scan = float(self.ui.load_pages.lineEdit_x1_scan.text())
        self.Pos_X2_Scan = float(self.ui.load_pages.lineEdit_x2_scan.text())

        self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text())
        #Update everything
        self.g_W=int((self.Pos_X2_Scan-self.Pos_X1_Scan)/self.cell_size)
        self.g_H=int((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.cell_size)

        #Create Graph
        self.color_grid_widget = ColorGrid(self.g_H,self.g_W,self.cell_size)
        self.ui.load_pages.Layout_table_Scan.addWidget(self.color_grid_widget)


        self.counter_Data_per_Pixel=0
        self.counter_Step_Zaber_X=0
        self.current_col=0
        self.current_row=0
        self.New_Color= [255,255,255]



        # Mover a X1, Y1 primero
        move_to_position(2,self.Pos_X1_Scan)
        move_to_position(0,self.Pos_Y1_Scan)
        check_position_and_start(0,self.Pos_Y1_Scan)

    def Scan_Continuos_X():

        self.counter_Data_per_Pixel=0
        self.speed = float(self.ui.load_pages.lineEdit_speed_ums.text())# / ((1.6381 / 1.9843))
        self.Pos_Y1_Scan = float(self.ui.load_pages.lineEdit_y1_scan.text())
        self.Pos_Y2_Scan = float(self.ui.load_pages.lineEdit_y2_scan.text())
        self.Pos_X1_Scan = float(self.ui.load_pages.lineEdit_x1_scan.text())
        self.Pos_X2_Scan = float(self.ui.load_pages.lineEdit_x2_scan.text())

        self.cell_size = int(self.ui.load_pages.lineEdit_Pixel_size.text())
        #Update everything
        self.g_W=int((self.Pos_X2_Scan-self.Pos_X1_Scan)/self.cell_size)
        self.g_H=int((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.cell_size)

        #Create Graph
        self.color_grid_widget = ColorGrid(self.g_H,self.g_W,self.cell_size)
        self.ui.load_pages.Layout_table_Scan.addWidget(self.color_grid_widget)


        self.counter_Data_per_Pixel=0
        self.counter_Step_Zaber_X=0
        self.current_col=0
        self.current_row=0
        self.New_Color= [255,255,255]

        # Mover a X1, Y1 primero
        move_to_position(0,self.Pos_Y1_Scan)
        move_to_position(2,self.Pos_X1_Scan)
        check_position_and_start_X(2,self.Pos_X1_Scan)

    #########################################################
    #########################################################

    def Change_Pixel_DAQ():
        #Stop condition
        #llego al final de una linea
        if self.counter_Data_per_Pixel >= (self.g_H):
            self.counter_Data_per_Pixel=0
            Stop_z1() #Paro el movimiento
            #Reinicio posiciones
            self.counter_Step_Zaber_X+=1
            new_x_pos=(self.Pos_X1_Scan+(((self.Pos_X2_Scan-self.Pos_X1_Scan)/self.g_W)*self.counter_Step_Zaber_X))
            if new_x_pos>=self.Pos_X2_Scan:
                print('------  Scan finished --------')
                self.Adquisit_Timer.stop()
            else:
                #Move to the next Position
                move_to_position(2,new_x_pos)
                move_to_position(0,self.Pos_Y1_Scan)
                check_position_and_start(0,self.Pos_Y1_Scan)
        else:
            #AVG the PSD and Weighted Moments
            self.dataAmp_Avg=(self.Freq_Data.mean(axis=1))
            print('N Avg Samples')
            print(self.Counter_DAQ_samples)
            self.PSD_Avg_Moment=(self.dataAmp_Avg*self.dataAmp_Avg)*(2/(self.number_of_samples*self.Laser_Frequency))
            #self.PSD_Avg_Moment = self.PSD_Avg_Moment[:n // 2]
            M0 = np.sum(self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])
            M1 = np.sum(self.dataFreq * self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0]) / M0
            print('AVG Moment')
            print(M1/M0)
            #Reinicio conteo data average y vector
            self.Counter_DAQ_samples=0
            self.Freq_Data=pd.DataFrame()
            self.New_Color=[0, int(((M1/M0))*255/48000), 0]


            self.color_grid_widget.changeCellColor(self.counter_Step_Zaber_X, self.counter_Data_per_Pixel, self.New_Color)
            self.counter_Data_per_Pixel+=1
            self.current_col= self.counter_Data_per_Pixel

            if self.counter_Data_per_Pixel >= self.g_H:
                self.counter_Data_per_Pixel += 1

    def Change_Pixel_DAQ_X():
        #Stop condition
        #llego al final de una linea
        if self.counter_Data_per_Pixel >= (self.g_W):
            self.counter_Data_per_Pixel=0
            Stop_z2() #Paro el movimiento
            #Reinicio posiciones
            self.counter_Step_Zaber_X+=1
            new_x_pos=(self.Pos_Y1_Scan+(((self.Pos_Y2_Scan-self.Pos_Y1_Scan)/self.g_H)*self.counter_Step_Zaber_X))
            if new_x_pos>=self.Pos_Y2_Scan:
                self.Adquisit_Timer.stop()
                self.color_grid_widget.exportar_Matrix_CSV()
                print('------  Scan finished --------')
                print('Maximum value detected')
                print(self.maximaxi)
                self.Data_Spectrum_Array.to_csv('Scanning_Avg_Spectrum.csv', index=True)
            else:
                move_to_position(0,new_x_pos)
                move_to_position(2,self.Pos_X1_Scan)
                check_position_and_start_X(2,self.Pos_X1_Scan)
        else:
            #AVG the PSD and Weighted Moments
            self.dataAmp_Avg=(self.Freq_Data.mean(axis=1))
            #Save Avg Spectrum
            self.Data_Spectrum_Array=pd.concat([self.Data_Spectrum_Array, self.dataAmp_Avg], axis=1)
            print('N Avg Samples')
            print(self.Counter_DAQ_samples)
            
            if self.dataAmp_Avg.empty:
                self.dataAmp_Avg=self.dataFreq*0
                self.Freq_Data=self.dataFreq*0
            #search the maximum peak detected
            #if self.maximaxi<max(self.Freq_Data.max()):
            #    self.maximaxi=max(self.Freq_Data.max())

            self.PSD_Avg_Moment=(self.dataAmp_Avg*self.dataAmp_Avg)*(2/(self.number_of_samples*self.Laser_Frequency))
            #self.PSD_Avg_Moment = self.PSD_Avg_Moment[:n // 2]
            M0 = np.sum(self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])
            # Solve division by 0
            if M0==0:
                M0=1
            M1 = np.sum(self.dataFreq * self.PSD_Avg_Moment) #* (self.dataFreq[1] - self.dataFreq[0])# / M0
            print('AVG Moment')
            print(M1/M0)
            #Reinicio conteo data average y vector
            self.Counter_DAQ_samples=0
            self.Freq_Data=pd.DataFrame()
            self.New_Color=[0, int(40000-(((M1/M0))*255/37000)), 0]

            self.color_grid_widget.changeCellColor(self.counter_Data_per_Pixel,self.counter_Step_Zaber_X, self.New_Color)
            
            self.color_grid_widget.updateCSV(self.counter_Step_Zaber_X-1,self.counter_Data_per_Pixel-1,(M1/M0),M0,M1)
            
            self.counter_Data_per_Pixel+=1
            self.current_col= self.counter_Data_per_Pixel

            if self.counter_Data_per_Pixel >= self.g_W:
                self.counter_Data_per_Pixel += 1



    def Capture_Data_Avg():
        

        ######### Update Laser data FFT and Voltage
        self.DAQ_Data=self.threadDAQ.DAQ_Data
        self.data_DAQ2=butter_bandpass_filter(self.DAQ_Data, self.low_freq_filter, self.high_freq_filter,self.order_filter, self.Laser_Frequency)
        self.dataAmp, self.dataFreq, _=FFT_calc(self.data_DAQ2, self.Laser_Frequency)

        #self.Freq_Data[self.Counter_DAQ_samples]=self.dataAmp
        amp=pd.Series((self.dataAmp))
        #print(max(amp))
        
        #Solo considero los datos si son mayores a 1755 peak sin flow
        #if (max(amp)>1000):
        self.Freq_Data=pd.concat([self.Freq_Data, amp], axis=1)
        
        self.Counter_DAQ_samples=self.Counter_DAQ_samples+1
        #print('timer')

        


    #########################################################
    #########################################################
    #MAXIMUM PEAK DETECTED
    self.maximaxi=0
    
    self.Data_Spectrum_Array=pd.DataFrame()

    self.Pixel_Interval_X = QTimer()
    self.Pixel_Interval_X.timeout.connect(Change_Pixel_DAQ_X)

    self.Pixel_Interval = QTimer()
    self.Pixel_Interval.timeout.connect(Change_Pixel_DAQ)

    self.Adquisit_Timer = QTimer()
    self.Adquisit_Timer.setInterval(1)
    self.Adquisit_Timer.timeout.connect(Capture_Data_Avg)


    self.ui.load_pages.Stop_x_but.clicked.connect(get_current_position)
    self.ui.load_pages.continuous_scanY_but.clicked.connect(Scan_Continuos_Y)
    self.ui.load_pages.continuous_scanX_but.clicked.connect(Scan_Continuos_X)
    self.ui.load_pages.Stop_Y_but.clicked.connect(Stop_z1)
    self.ui.load_pages.Stop_x_but.clicked.connect(Stop_z2)



    #########################################################
    #########################################################
            
    #########################################################
    #########################################################

    #########################################################
    #########################################################
    



   