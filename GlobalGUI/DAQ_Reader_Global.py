

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

import Thread_DAQ_single as tds

import pandas as pd



def Set_DAQ_Functions(self):


    def Update_DAQ_Params(self):
        self.Laser_Frequency = float(self.ui.load_pages.lineEdit_Laser.text())

        #self.fileSave=int(self.ui.load_pages.lineEdit_FileSave.text())
        self.fileSave=int(2)
        self.number_of_samples=int(self.ui.load_pages.lineEdit_number_samples.text())
        self.DAQ_Device="Dev1/ai0"

        # Band Pass Filter Params
        self.order_filter=4
        self.low_freq_filter=float(self.ui.load_pages.lineEdit_Low_Freq.text())
        self.high_freq_filter=float(self.ui.load_pages.lineEdit_High_Freq.text())
        
        
        self.Directory=(self.ui.load_pages.lineEdit_Directory.text())
        self.FileName=(self.ui.load_pages.lineEdit_Name_Files.text())
        self.Amp_Peak_Search=float(self.ui.load_pages.lineEdit_amp_peak.text())

        #RMS average
        self.CounterAvg=0
        self.VectorsAvg=int(self.ui.load_pages.lineEdit_Avg_FFT.text()) # Graph hold peaks
        self.Freq_Data=pd.DataFrame()
        
        #Save Data
        self.CounterPeaks=0
        self.exten=".npy"
        self.number_File=0


        0.155

    Update_DAQ_Params(self)


    def Init_DAQ_Connection():
        Update_DAQ_Params(self)
        # Creation of the thread
        print("------ DAQ Thread Init -------")
        try:
            self.threadDAQ = tds.DAQData(self.fileSave, self.Laser_Frequency, self.number_of_samples, self.DAQ_Device,self.fileSave)
            self.DAQ_Data= self.threadDAQ.DAQ_Data
            self.DAQ_X_Axis=self.threadDAQ.DAQ_X_Axis
            self.DAQ_X_Axis=np.array(self.DAQ_X_Axis)*1000/(self.Laser_Frequency)
            print("------ DAQ Reading Mode: On -------")
        except:
            print('------- DAQ init Failed  ---------')


    def Stop_DAQ():
        self.threadDAQ.deleteDAQ()
        #self.timerPLOT.stop()
        print("------ DAQ Reading Mode: Off -------")



    #Update DAQ Parameters in TAB DAQ
    self.ui.load_pages.DAQ_connect_but.clicked.connect(Init_DAQ_Connection)
    
    #Update DAQ Parameters in TAB Calib
    self.ui.load_pages.continuous_scanX_but.clicked.connect(Init_DAQ_Connection)
    self.ui.load_pages.continuous_scanY_but.clicked.connect(Init_DAQ_Connection)
    self.ui.load_pages.Step_Step_but.clicked.connect(Init_DAQ_Connection)
    #Stop DAQ

    self.ui.load_pages.Stop_x_but.clicked.connect(Stop_DAQ) 
    self.ui.load_pages.Stop_Y_but.clicked.connect(Stop_DAQ) 


    self.ui.load_pages.Stop_DAQ_but.clicked.connect(Stop_DAQ) 

