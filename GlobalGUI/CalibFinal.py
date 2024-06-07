from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import *
import pyqtgraph as pg
import sys
from random import randint

from PySide6 import QtCore
# Libraries
from nidaqmx.stream_readers import AnalogSingleChannelReader
import nidaqmx as ni
from nidaqmx import constants
from nidaqmx import stream_readers
import numpy as np
import pandas as pd
import matlab.engine

import zaber_motion
from zaber_motion import Units
from zaber_motion.binary import Connection,CommandCode

import time

import numpy as np
from numpy import trapz
from scipy.signal import welch, get_window
from scipy.fft import rfft, rfftfreq

import numpy as np
from scipy.signal import butter,filtfilt


# Zaber
COM_4="COM4"

# Laser sample frequency [Hz]
# Laser sample frequency [Hz]
Laser_frequency = 2000000 #500000
number_of_samples= 16384# 0.5s 2'12


#Dataframe creation
df = pd.DataFrame(columns=['Zaber_pos','Percen','F_avg','M1','M0','F_avg_noise','M1_noise','M0_noise'])
#Folder of Data
directory='./DataEXP/Peaks/calib10p_4um_3exp/'
exten=".npy"
nameFiles="Calib"
number=0
#Steps
counter=0
#Device
ZaberDev=2

Steps=np.linspace(start=42420, stop=42650, num=20)#12

def butter_highpass_filter(data, cutoff, fs, order, text2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=text2, analog=False)
    y = filtfilt(b, a, data)
    return y


class GraphTest(QMainWindow):
    def __init__(self):
        super().__init__()
        
        pen1 = pg.mkPen(color=(255, 0, 0))
        pen2 = pg.mkPen(color=(0, 0, 0))
        pen3 = pg.mkPen(color=(0, 0, 0))

        self.graphWidget = pg.GraphicsLayoutWidget()
        self.graphWidget.setBackground('w')
        self.setCentralWidget(self.graphWidget)
        
        self.p1 = self.graphWidget.addPlot(row=0, col=0)
        self.p2 = self.graphWidget.addPlot(row=1, col=0)
        self.p3 = self.graphWidget.addPlot(row=2, col=0)

        self.x = list(range(number_of_samples))  
        self.y = list(range(number_of_samples))  
        self.dataFreq = list(range(number_of_samples))  
        self.dataFreqY = list(range(number_of_samples))  
        self.dataFFTX = list(range(number_of_samples))  
        self.dataFFTY = list(range(number_of_samples))  

        
        self.data_Time =  self.p1.plot(self.x, self.y, pen=pen1)
        self.data_Freq =  self.p2.plot(self.dataFreq, self.dataFreqY, pen=pen2)
        self.data_Freq.setLogMode(False, True)
        self.data_FFT =  self.p3.plot(self.dataFFTX, self.dataFFTY, pen=pen3)


        self.timerPLOT = QTimer()
        self.timerPLOT.setInterval(1/2000)
        self.timerPLOT.timeout.connect(self.update_plot_data)
        #self.timerPLOT.start()

        self.timerADQ = QTimer()
        self.timerADQ.setInterval(1/250000)
        self.timerADQ.timeout.connect(self.data_adquisition)
        #self.timerADQ.start()

        #### Zaberz ###############################
        self.timerZab = QTimer()
        self.timerZab.setInterval(2)
        self.timerZab.timeout.connect(self.move_Zaber)
        self.timerZab.start()

        self.timerWait = QTimer()
        self.timerWait.setInterval(2000)
        self.timerWait.timeout.connect(self.wait_time)
        #self.timerWait.start()

        #Parameters ########################### DATA
        self.data_DAQ = np.zeros(number_of_samples, dtype=np.float64)

        self.Window = get_window('hamming', len(self.data_DAQ))
        #RMS average
        self.CounterRMS=0

        self.VectorsRMS=10
        self.contadorinf=0

        self.vectors = [np.zeros(number_of_samples) for _ in range(self.VectorsRMS)]

        #Parameters ########################### Zaber
        self.ActualStep=0
        self.Zaber_Pos=0
        # Reset Zaber to cero position
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            #device_list[2].home()
            #device_list[0].home()
            #device_list[1].home()


    def FreqSpectrum(self):

        
        self.data_DAQ2=butter_highpass_filter(self.data_DAQ, 20000, Laser_frequency, 3, "high")
        #4000
        self.data_DAQ2=butter_highpass_filter(self.data_DAQ2, 400000, Laser_frequency, 3, "low")

        self.vectors[self.CounterRMS] = self.data_DAQ
        self.CounterRMS=self.CounterRMS+1
        self.contadorinf=self.contadorinf+1
        if self.CounterRMS==self.VectorsRMS:
            
            self.timerADQ.stop()
            self.timerPLOT.stop()
            self.CounterRMS=0
        
            #RMS average
            FreqData=np.sqrt(np.mean(np.square(self.vectors), axis=0))

            #FFT
            yf = rfft(self.data_DAQ)
            xf = rfftfreq(number_of_samples, 1 / Laser_frequency)
            yf=np.abs(yf)
            self.dataFFTX=xf
            self.dataFFTY=yf

            #res = np.mean(FreqData.reshape(-1, ), axis=1)
            #PSD
            self.dataFreq,self.dataFreqY = welch(FreqData, fs=Laser_frequency, window = self.Window)
            
            window_size = 5
            window = np.ones(window_size) / window_size
            self.dataFreqY = np.convolve(self.dataFreqY, window, mode='valid')
            self.dataFreq = np.convolve(self.dataFreq, window, mode='valid')
            
            
            frequencies=self.dataFreq[:4000]
            psd=self.dataFreqY[:4000]

            positionCm=round(float(self.Zaber_Pos)*100/1039370,5)
            #m0 = round(abs(trapz(frequencies,psd)*1000),5)
            #m1 = round(abs(trapz(frequencies,frequencies*psd)),5); #Calculate first moment

            #Processing
            #with open(str(directory+"ValuesData.txt"), 'a') as file:
            #    file.write("Pos: "+str(positionCm)+" M0: "+str(m0)+" M1: "+str(m1)+ '\n')



            self.update_plot_data()
            self.timerZab.start()




        #with open('./DataEXP/noisedata.npy', 'wb') as f:
            

        #directory='./DataEXP/'
        #exten=".npy"
        #nameFiles="MilkExp"
        number=self.CounterRMS

        positionCm=round(float(self.Zaber_Pos)*100/1039370,5)

        np.save(directory+nameFiles+"_"+str(positionCm)+"_"+str(number)+'_'+str(self.contadorinf)+exten, self.data_DAQ)



        #with open('noisedata.npy', 'rb') as f:
        #    noiseData = np.load(f)

        #self.dataFreqY=self.dataFreqY-noiseData

    def data_adquisition(self):

        with ni.Task() as task_Laser:
            #Signal Adquisition ########################################################
            #Add Sensor
            task_Laser.ai_channels.add_ai_voltage_chan("Dev2/ai0",max_val=5, min_val=-5)
            # Set Sampling clocks
            task_Laser.timing.cfg_samp_clk_timing(rate=Laser_frequency, sample_mode=constants.AcquisitionType.CONTINUOUS)
            #Initialize Stream reader
            reader = AnalogSingleChannelReader(task_Laser.in_stream)
            # Acquire and store in read_array
            reader.read_many_sample(self.data_DAQ, number_of_samples_per_channel=number_of_samples,timeout=10.0)

        #self.data_DAQ = np.random.randint(1,101,number_of_samples)
        if self.ActualStep<len(Steps):
            self.FreqSpectrum()
            
    def update_plot_data(self):

        self.x = list(range(number_of_samples))

        self.data_Time.setData(self.x, self.data_DAQ)
        self.data_Freq.setData(self.dataFreq, self.dataFreqY)
        self.data_FFT.setData(self.dataFFTX, self.dataFFTY)



    def move_Zaber(self):
        self.timerZab.stop()
        with Connection.open_serial_port(COM_4) as connection:
            device_list = connection.detect_devices()
            #device_list[2].home()
            print(Steps)
            if self.ActualStep<len(Steps):
                new_position=Steps[self.ActualStep]
                #new_position=42175
                zaber_pos=new_position/10000
                device_list[ZaberDev].move_absolute(float(zaber_pos), Units.LENGTH_CENTIMETRES)
                print("---------- Move Zaber ---------- " + str(Steps[self.ActualStep])+" ----------")
                self.Zaber_Pos=round((float(device_list[ZaberDev].get_position())*100/1039370),4)
                
                self.ActualStep=self.ActualStep+1
                self.timerWait.start()
            else:
                self.ActualStep=0
                self.timerADQ.start()
                self.timerPLOT.start()

    def wait_time(self):
        self.timerWait.stop()
        self.timerADQ.start()
        self.timerPLOT.start()





app = QApplication(sys.argv)
main = GraphTest()
main.show()
app.exec()

