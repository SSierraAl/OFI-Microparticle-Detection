from random import randint
import numpy as np
import pyqtgraph as pg
from nidaqmx.stream_readers import AnalogSingleChannelReader
import nidaqmx as ni
from nidaqmx import constants
from nidaqmx import stream_readers
from PySide6.QtCore import QTimer




#Define all DAQ parameters
def SetDAQParams(self):
    self.DAQ_Freq=250000
    self.DAQ_Device="Dev2/ai0"
    self.DAQ_Num_Samples=524288
    self.DAQ_X_Axis = list(range(self.DAQ_Num_Samples))
    self.DAQ_Data = np.zeros(self.DAQ_Num_Samples, dtype=np.float64)



    def RequestDAQData():

        with ni.Task() as task_Laser:
            #Signal Adquisition ########################################################
            #Add Sensor
            task_Laser.ai_channels.add_ai_voltage_chan(self.DAQ_Device,max_val=5, min_val=-5)
            # Set Sampling clocks
            task_Laser.timing.cfg_samp_clk_timing(rate=self.DAQ_Freq, sample_mode=constants.AcquisitionType.CONTINUOUS)
            #Initialize Stream reader
            reader = AnalogSingleChannelReader(task_Laser.in_stream)
            # Acquire and store in read_array
            reader.read_many_sample(self.DAQ_Data, number_of_samples_per_channel=self.DAQ_Num_Samples,timeout=10.0)

            # Pending !!!!!
            self.DAQ_X_Axis = list(range(self.DAQ_Num_Samples))
            print("Leo el DAQ")



    #Timer Adquisition
    self.timerDAQ = QTimer()
    self.timerDAQ.setInterval(1/10)
    self.timerDAQ.timeout.connect(RequestDAQData)
