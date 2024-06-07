
import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode
from random import randint
import numpy as np
import pyqtgraph as pg
import pickle
from PySide6.QtCore import QTimer
import time
from scipy.signal import welch, get_window
from Frequency_Func import *


def InsertHomeGraphs(self):

    # Array to save all the data to write, DAQ data adquisition
    self.vectors2 = [np.zeros(int(self.number_of_samples)) for _ in range(self.fileSave)]
    # Creation of the arrays to use in the graphs
    self.Volx= np.array(list(range(self.number_of_samples)))*((self.number_of_samples)/(self.Laser_Frequency))
    self.Voly = [randint(0,100) for _ in range(self.number_of_samples)]


     # Creation of the Voltage Laser Graph
    self.voltageGraph = pg.PlotWidget()
    # Title of the Graph
    self.voltageGraph.setTitle("Laser Signal")
    # Label of the bottom
    self.voltageGraph.setLabel('bottom', "Time(ms)")   
    # left label     
    self.voltageGraph.setLabel('left', "Voltage (V)")
    # Set the color of the background
    self.voltageGraph.setBackground('w')
    # Set the color of the line (Blue)
    pen = pg.mkPen(color=(0, 153, 153))
    # Creation of the line to put in the Voltage Laser Graph
    self.data_line_Vol =  self.voltageGraph.plot(self.Volx, self.Voly, pen=pen)
    #Widget Creation
    # Creation of the FFT Laser Graph
    self.freqGraph = pg.PlotWidget()
    self.freqGraph.setTitle("Frequency Signal")
    self.freqGraph.setLabel('bottom', "Freq (Hz)")  
    self.freqGraph.setLabel('left', "Amplitude")
    self.dataFreq = list(range(1000))  
    self.dataAmp = [randint(0,100) for _ in range(1000)]  
    self.freqGraph.setBackground('w')
    pen2 = pg.mkPen(color=(64, 64, 64))
    self.data_Freq =  self.freqGraph.plot(self.dataFreq, self.dataAmp, pen=pen2)

    #Widget Creation
    # Creation of the AVG FFT Laser Graph
    self.freqGraph_AVG = pg.PlotWidget()
    self.freqGraph_AVG.setTitle("Frequency Signal Avg")
    self.freqGraph_AVG.setLabel('bottom', "Freq (Hz)")  
    self.freqGraph_AVG.setLabel('left', "Amplitude")
    self.dataAmp_Freq = list(range(1000))  
    self.dataAmp_Avg = [randint(0,100) for _ in range(1000)]  
    self.freqGraph_AVG.setBackground('w')
    pen3 = pg.mkPen(color=(0, 0, 255))
    self.data_Freq_AVG =  self.freqGraph_AVG.plot(self.dataAmp_Freq, self.dataAmp_Avg, pen=pen3)



     
    #Insert Graphs
    self.ui.load_pages.LayoutGraphics.addWidget(self.voltageGraph)
    self.ui.load_pages.LayoutGraphics.addWidget(self.freqGraph)
    self.ui.load_pages.LayoutGraphics.addWidget(self.freqGraph_AVG)



    # Adquisiton Particles Mode ON

    self.Particle_Search=False
    self.calibration_check=False





    def updatePlotData_home():
        # Original Voltage
        #self.data_line_Vol.setData(self.DAQ_X_Axis, self.DAQ_Data)
        #Plot with Filter
        self.data_line_Vol.setData(self.DAQ_X_Axis, self.data_DAQ2)
        self.data_Freq.setData(self.dataFreq, self.dataAmp)
        self.data_Freq_AVG.setData(self.dataFreq, self.dataAmp_Avg)




    def data_adquisition_home():

        ######### Update Laser data FFT and Voltage
        self.DAQ_Data=self.threadDAQ.DAQ_Data
        self.data_DAQ2=butter_bandpass_filter(self.DAQ_Data, self.low_freq_filter, self.high_freq_filter,self.order_filter, self.Laser_Frequency)
        self.dataAmp, self.dataFreq, _=FFT_calc(self.data_DAQ2, self.Laser_Frequency)

        if self.CounterAvg<self.VectorsAvg:
            self.Freq_Data[self.CounterAvg]=self.dataAmp
            self.CounterAvg=self.CounterAvg+1
        else:
            self.CounterAvg=0

            #Max Peak detected
            self.ui.load_pages.Max_Peak_val.setText(str(round(max(self.dataAmp_Avg),2)))
            self.PSD_Avg_Moment=(self.dataAmp_Avg*self.dataAmp_Avg)*(2/(self.number_of_samples*self.Laser_Frequency))
            M0 = np.sum(self.PSD_Avg_Moment)
            if M0==0:
                M0=1
            M1 = np.sum(self.dataFreq * self.PSD_Avg_Moment)
            self.ui.load_pages.Moment_val.setText(str(round((M1/M0),2)))


            
        self.dataAmp_Avg=(self.Freq_Data.mean(axis=1))



        # Particle Search
        #################################################
        if self.Particle_Search==True:
            if (max(self.dataAmp)>=self.Amp_Peak_Search):
                self.CounterPeaks=self.CounterPeaks+1
                print(max(self.dataAmp))
                print(self.CounterPeaks)
                np.save(self.Directory+self.FileName+"_"+str(self.number_file)+'_'+str(self.CounterPeaks)+self.exten, self.DAQ_Data)
            

        # Particle Search
        #################################################
        if self.calibration_check==True:
            if self.Zaber_Adquisition==True:
            
                if self.CounterCheck<self.Data_To_Check:
                    self.CounterCheck=self.CounterCheck+1
                    if (max(self.dataAmp)>=self.Amp_Peak_Search):
                        self.CounterPeaks=self.CounterPeaks+1
                        print(max(self.dataAmp))
                        print(self.CounterPeaks)
                        np.save(self.Directory+self.FileName+"_Calib_"+str(self.Zaber_Pos) +'_'+str(self.number_File)+'_'+str(self.CounterPeaks)+self.exten, self.DAQ_Data)
            
                else:
                    print('------- ' +str(self.Zaber_Pos)+' / '+str(self.Zaber_Steps[self.ActualStep-1])+ ' Number of Peaks: '+str(self.CounterPeaks)+' --------' )
                    self.CounterCheck=0
                    self.CounterPeaks=0
                    self.Zaber_Adquisition=False
                    self.Zaber_Ready=False




    self.timerPLOT = QTimer()
    self.timerPLOT.setInterval(40)
    self.timerPLOT.timeout.connect(updatePlotData_home)

    self.timerADQ = QTimer()
    self.timerADQ.setInterval(1)
    self.timerADQ.timeout.connect(data_adquisition_home)
    


    def Init_Home_Plots():
        self.timerADQ.start()
        self.timerPLOT.start()

    def Stop_Home_Plots():
        self.timerADQ.stop()
        self.timerPLOT.stop()
    
    self.ui.load_pages.DAQ_connect_but.clicked.connect(Init_Home_Plots)
    self.ui.load_pages.Stop_DAQ_but.clicked.connect(Stop_Home_Plots) 




    ##############################################
    # Particle Detection
    ##############################################

    def Start_Search_Particle():

        self.Directory=(self.ui.load_pages.lineEdit_Directory.text())
        self.FileName=(self.ui.load_pages.lineEdit_Name_Files.text())
        self.Amp_Peak_Search=float(self.ui.load_pages.lineEdit_amp_peak.text())

        self.CounterPeaks=0
        self.number_file=0

        self.Particle_Search=True

    def Stop_Search_Particle():
        self.CounterPeaks=0
        self.number_file=0
        self.Particle_Search=False

    self.ui.load_pages.Search_Particles_but.clicked.connect(Start_Search_Particle) 
    self.ui.load_pages.Stop_Search_P_but.clicked.connect(Stop_Search_Particle)



    ##############################################
    # Zaber Calibration
    ##############################################

 
                    

    def Start_Zaber_Calib_Home():

        self.Directory=(self.ui.load_pages.lineEdit_Directory.text())
        self.FileName=(self.ui.load_pages.lineEdit_Name_Files.text())

        self.Amp_Peak_Search=float(self.ui.load_pages.lineEdit_amp_peak.text())

        #Parameters ########################### Zaber
        zab_start=int(self.ui.load_pages.lineEdit_start_zab_pos.text())
        zab_stop=int(self.ui.load_pages.lineEdit_end_zab_pos.text())
        zab_steps=int(self.ui.load_pages.lineEdit_steps_zab.text())
        self.Data_To_Check=int(self.ui.load_pages.lineEdit_zab_samplesCheck.text())
        

        self.Zaber_Steps=np.linspace(start=zab_start, stop=zab_stop, num=zab_steps)
        self.ActualStep=0
        self.Zaber_Pos=0

        self.Zaber_Ready=False
        self.ZaberDev=2
        
        self.calibration_check=True
        self.Zaber_Adquisition=True
        
        self.CounterCheck=0

        def move_Zaber():
                if self.Zaber_Ready==False:
                    with Connection.open_serial_port(self.Zaber_COM) as connection:
                        device_list = connection.detect_devices()
                        if self.ActualStep<len(self.Zaber_Steps):
                            new_position=self.Zaber_Steps[self.ActualStep]
                            zaber_pos=new_position/10000
                            device_list[self.ZaberDev].move_absolute(float(zaber_pos), Units.LENGTH_CENTIMETRES)
                            print("---------- Move Zaber ---------- " + str(self.Zaber_Steps[self.ActualStep])+" ----------")
                            self.Zaber_Pos=round((float(device_list[self.ZaberDev].get_position())*100/1039370),4)
                            self.ActualStep=self.ActualStep+1

                            self.Zaber_Ready=True
                            print('--- move zaber finish ---')
                        else:
                            print("-------- Scan Finished --------")
                            self.calibration_check=False
                            self.timerWait.stop()
        
                elif self.Zaber_Ready==True:
                        print('--- acquire zaber data ---')
                        self.Zaber_Adquisition = True
                        self.Zaber_Ready=2
                else:
                    pass

        self.timerWait = QTimer()
        self.timerWait.setInterval(2000)
        self.timerWait.timeout.connect(move_Zaber)
        self.timerWait.start()


        # Reset Zaber to cero position
        with Connection.open_serial_port(self.Zaber_COM) as connection:
            device_list = connection.detect_devices()
            #device_list[1].home()
            device=device_list[2]
            #device.home()
            device.move_absolute(float(3.8357), Units.LENGTH_CENTIMETRES) #4.21024 4.642857


    self.ui.load_pages.Start_Zaber_Calib_but.clicked.connect(Start_Zaber_Calib_Home)

