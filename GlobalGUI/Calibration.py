
# Usefull Links                                                                                    
#https://nidaqmx-python.readthedocs.io/en/latest/
#https://fr.mathworks.com/help/matlab/matlab_external/connect-python-to-running-matlab-session.html

# Libraries
from nidaqmx.stream_readers import AnalogSingleChannelReader
import nidaqmx as ni
from nidaqmx import constants
from nidaqmx import stream_readers
import numpy as np



import time

# Zaber
COM_4="COM3"

# Laser sample frequency [Hz]
Laser_frequency = 500000
number_of_samples=4096 # 0.5s


#Steps
counter=0
Steps=np.linspace(start=38000, stop=43000, num=600)
DAQ_Data = np.zeros(number_of_samples, dtype=np.float64)


with ni.Task() as task_Laser:
    # Signal Acquisition
    task_Laser.ai_channels.add_ai_voltage_chan("Dev2/ai0", max_val=5, min_val=-5)
    
    # Configure sampling clock with increased buffer size
    task_Laser.timing.cfg_samp_clk_timing(rate=Laser_frequency, 
                                          sample_mode=constants.AcquisitionType.CONTINUOUS,
                                          samps_per_chan=number_of_samples * 10)

    # Initialize Stream reader
    reader = AnalogSingleChannelReader(task_Laser.in_stream)

    while True:
        start_time = time.time()
        reader.read_many_sample(DAQ_Data, number_of_samples_per_channel=number_of_samples, timeout=10)
        end_time = time.time()
        print(f"Read time: {end_time - start_time:.4f} seconds")
        print(DAQ_Data)