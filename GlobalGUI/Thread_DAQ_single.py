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
    completeddaq = Signal(np.ndarray)
    # Function of initilisation of the class worker
    def __init__(self,Laser_frequency,Number_to_mean,DAQ_Device,number_of_samples,fileSave):
        #Important to self-beggining the worker
        super().__init__()
        # Definition of all variables needed to take the data and do the coms with NI DAQ
        self.Laser_frequency=Laser_frequency
        self.Number_to_mean=int(Number_to_mean)
        #self.DAQ_Device=DAQ_Device  #"Dev1/ai0" OLD IMPLEMN
        self.DAQ_Device= DAQ_Device #"Dev1/ai0"
        self.number_of_samples=int(number_of_samples)
        # Variables to store the most important info
        self.DAQ_X_Axis = list(range(self.number_of_samples))
        self.DAQ_Data = np.zeros(self.number_of_samples, dtype=np.float64)
        # Number of files
        self.fileSave=fileSave
        self.running = True
        print("INFO: DAQ: new workerDAQ created and started")


    @Slot()
    def run(self):
        with nidaqmx.Task() as task_Laser:
            #Signal Adquisition ########################################################
            #Add Sensor
            print(f"INFO: Selected DAQ device: {self.DAQ_Device} ")
            task_Laser.ai_channels.add_ai_voltage_chan(self.DAQ_Device,max_val=5, min_val=-5)
            # Set Sampling clocks
            task_Laser.timing.cfg_samp_clk_timing(rate=self.Laser_frequency, sample_mode=constants.AcquisitionType.CONTINUOUS)
            #Initialize Stream reader
            reader = AnalogSingleChannelReader(task_Laser.in_stream)

            while self.running:
                try:
                    #print("DEBUG: workerDAQ retrieving samples")
                    reader.read_many_sample(self.DAQ_Data, number_of_samples_per_channel=self.number_of_samples, timeout=10)
                    self.completeddaq.emit(self.DAQ_Data)  # Emitting data read from DAQ
                except:
                    print("ERROR: workerDAQ failed to retrieve samples")
                    pass

    def stop(self):
        self.running = False 
        
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

        # Creation of the worker linked to this class
        self.workerDAQ = WorkerDAQ(self.Laser_frequency,self.Number_to_mean,self.DAQ_Device,self.number_of_samples,self.fileSave)
        self.threadDAQ = QThread()  # Corrected thread name
        self.workerDAQ.moveToThread(self.threadDAQ)
        self.workerDAQ.completeddaq.connect(self.completedaq)
        self.threadDAQ.started.connect(self.workerDAQ.run)
        self.threadDAQ.start()

    # Function to copy the data when it's done   
    def completedaq(self, data):
        self.DAQ_Data=data

    #Function to delete the thread.
    def deleteDAQ(self):
        self.workerDAQ.stop()
        self.threadDAQ.quit()
        self.threadDAQ.wait()
        # Reset the DAQ Device
        system = nidaqmx.system.System.local()
        for device in system.devices:
            #if device.name == self.DAQ_Device:
            device.reset_device()
            print(f"Device {self.DAQ_Device} has been reset.")

