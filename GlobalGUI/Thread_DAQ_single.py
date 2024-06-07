###########################################################################################################################
################################################# Libraries ###############################################################
###########################################################################################################################
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtCore import QTimer

import numpy as np

from nidaqmx.stream_readers import AnalogSingleChannelReader
import nidaqmx as ni
import nidaqmx.system
from nidaqmx import constants

############################################################################################################################
######################################## Thread DAQ ########################################################################
############################################################################################################################

#Class Worker, it's who gonna do the process of adquisition in the background
class WorkerDAQ(QObject):
    # signal of finish process
    completeddaq = Signal(int)
    # Function of initilisation of the class worker
    def __init__(self,Laser_frequency,Number_to_mean,DAQ_Device,number_of_samples,fileSave):
        #Important to self-beggining the worker
        super().__init__()
        # Definition of all variables needed to take the data and do the coms with NI DAQ
        self.Laser_frequency=Laser_frequency
        self.Number_to_mean=int(Number_to_mean)
        self.DAQ_Device=DAQ_Device  #"Dev1/ai0"
        self.number_of_samples=int(number_of_samples)
        # Variables to store the most important info
        self.DAQ_X_Axis = list(range(self.number_of_samples))
        self.DAQ_Data = np.zeros(self.number_of_samples, dtype=np.float64)
        # Number of files
        self.fileSave=fileSave
        
    # Function of adquisition
    
    @Slot(int)
    def RequestDAQData(self):
        j=1
        #Question to know if we have information to transfert
        with ni.Task() as task_Laser:
            #Signal Adquisition ########################################################
            #Add Sensor
            task_Laser.ai_channels.add_ai_voltage_chan(self.DAQ_Device,max_val=5, min_val=-5)
            # Set Sampling clocks
            task_Laser.timing.cfg_samp_clk_timing(rate=self.Laser_frequency, sample_mode=constants.AcquisitionType.CONTINUOUS)
            #Initialize Stream reader
            reader = AnalogSingleChannelReader(task_Laser.in_stream)
            # Acquire and store in read_array = self.DAQ_Data

            reader.read_many_sample(self.DAQ_Data, number_of_samples_per_channel=self.number_of_samples,timeout=10)         

        #self.DAQ_X_Axis = list(range(self.number_of_samples))
        # Emit the complete signal
        self.completeddaq.emit(j)

        #print('request data daq')

# creation of the Class DAQData, an object linked to the worker and the master class of the thread
        
class DAQData(QObject):
    # Creation of the requested thread of the worker
    workDAQ_requested = Signal(int)
    # Function of initilisation of the class DAQData
    def __init__(self,Number_to_mean,Laser_frequency,number_of_samples, DAQ_Device,fileSave):
        #Important to self-beggining the DAQData
        super().__init__()
        # Number of files
        self.fileSave=fileSave
        # Definition of all variables needed to take the data and do the coms with NI DAQ
        self.Number_to_mean=Number_to_mean
        self.Laser_frequency=Laser_frequency
        self.number_of_samples=number_of_samples
        self.DAQ_Device=DAQ_Device
        # Variables to store the most important info
        self.DAQ_X_Axis= list(range(int(self.number_of_samples)))
        self.DAQ_Data = np.zeros(int(self.number_of_samples), dtype=np.float64)

        
        self.PleaseStop=False

        # Creation of the worker linked to this class
        self.workerDAQ = WorkerDAQ(self.Laser_frequency,self.Number_to_mean,self.DAQ_Device,self.number_of_samples,self.fileSave)
        # Creation of the thread
        self.worker_threadDAQ = QThread()       
        # Connect the worker with our function complete once finish process
        self.workerDAQ.completeddaq.connect(self.completedaq)
        # Connect the signal with the signal in the worker
        self.workDAQ_requested.connect(self.workerDAQ.RequestDAQData)
        # Copy all the worker to a thread
        self.workerDAQ.moveToThread(self.worker_threadDAQ)
        # start the thread
        self.worker_threadDAQ.start()

        self.workDAQ_requested.emit(0)

    # Function to copy the data when it's done   
    def completedaq(self):
        
        self.DAQ_Data=(self.workerDAQ.DAQ_Data)
        self.DAQ_X_Axis=self.workerDAQ.DAQ_X_Axis
        #print('read')


        self.workDAQ_requested.emit(5)
    
    #Function to delete the thread.
    def deleteDAQ(self):
        while(self.worker_threadDAQ.isFinished()==False):
            #self.worker_threadDAQ.wait() 
            self.worker_threadDAQ.terminate()
            print('---- Thread deleted -----')
        # Reset the DAQ Device
        system = nidaqmx.system.System.local()
        for device in system.devices:
            #if device.name == self.DAQ_Device:
            device.reset_device()
            print(f"Device {self.DAQ_Device} has been reset.")

