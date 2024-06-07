
# Usefull Links                                                                                    
#https://nidaqmx-python.readthedocs.io/en/latest/
#https://fr.mathworks.com/help/matlab/matlab_external/connect-python-to-running-matlab-session.html

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

# Zaber
COM_4="COM4"

# Laser sample frequency [Hz]
Laser_frequency = 1000000
number_of_samples=4026 # 0.5s


#Matlab engine connection
eng = matlab.engine.connect_matlab()
#Dataframe creation
df = pd.DataFrame(columns=['Zaber_pos','Percen','F_avg','M1','M0','F_avg_noise','M1_noise','M0_noise'])

#Steps
counter=0
Steps=np.linspace(start=38000, stop=43000, num=600)
print(Steps)

with ni.Task() as task_Laser:
    #Signal Adquisition ########################################################
    #Add Sensor
    task_Laser.ai_channels.add_ai_voltage_chan("Dev1/ai0",max_val=3, min_val=-3)
    # Set Sampling clocks
    task_Laser.timing.cfg_samp_clk_timing(rate=Laser_frequency, sample_mode=constants.AcquisitionType.FINITE)
    #Initialize Stream reader
    reader = AnalogSingleChannelReader(task_Laser.in_stream)

    #Zaber Aligment ########################################################
    with Connection.open_serial_port(COM_4) as connection:
        device_list = connection.detect_devices()
        device_list[2].home()
        #Maximum zaber position
        for i in Steps:
            #zaber_pos=float(i*4.95/1039370)
            zaber_pos=i/10000
            device_list[2].move_absolute(float(zaber_pos), Units.LENGTH_CENTIMETRES)
            #time.sleep(2)
            print("---------- Capturing Data ---------- " + str(len(Steps)-counter)+" ----------")
            # initialize data array
            read_array = np.zeros(number_of_samples, dtype=np.float64)
            # Acquire and store in read_array
            reader.read_many_sample(read_array, number_of_samples_per_channel=number_of_samples,timeout=10.0)
            #PWelch ########################################################
            #f_avg, m0, 01

            f_avg=eng.func_Pwelch(read_array)

            percen=np.percentile(read_array, 90)
            # Append rows ########################################################
            #df = df.append({'Zaber_pos':f_avg[0][0], 'F_avg':f_avg[0][0], 'M0':f_avg[0][1], 'M1':f_avg[0][2]},ignore_index = True)
            posZab=device_list[2].get_position()
            df = pd.concat([df, pd.DataFrame.from_records([{'Zaber_pos':posZab,'Percen':percen, 'F_avg':f_avg[0][0], 'M1':f_avg[0][1], 'M0':f_avg[0][2], 'F_avg_noise':f_avg[0][3], 'M1_noise':f_avg[0][4], 'M0_noise':f_avg[0][5]}])], ignore_index=True)
            
            
            ##################### Data 1 ################################
                        # initialize data array
            read_array = np.zeros(number_of_samples, dtype=np.float64)
            # Acquire and store in read_array
            reader.read_many_sample(read_array, number_of_samples_per_channel=number_of_samples,timeout=10.0)
            # print results
            print(max(read_array))
            print(min(read_array))
            #PWelch ########################################################
            #f_avg, m0, 01
            f_avg=eng.func_Pwelch(read_array)
            percen=np.percentile(read_array, 90)
            # Append rows ########################################################
            #df = df.append({'Zaber_pos':f_avg[0][0], 'F_avg':f_avg[0][0], 'M0':f_avg[0][1], 'M1':f_avg[0][2]},ignore_index = True)
            posZab=device_list[2].get_position()
            df = pd.concat([df, pd.DataFrame.from_records([{'Zaber_pos':posZab,'Percen':percen, 'F_avg':f_avg[0][0], 'M1':f_avg[0][1], 'M0':f_avg[0][2], 'F_avg_noise':f_avg[0][3], 'M1_noise':f_avg[0][4], 'M0_noise':f_avg[0][5]}])], ignore_index=True)
            
            
            ##################### Data 2 ################################
            # initialize data array
            read_array = np.zeros(number_of_samples, dtype=np.float64)
            # Acquire and store in read_array
            reader.read_many_sample(read_array, number_of_samples_per_channel=number_of_samples,timeout=10.0)
            # print results
            print(max(read_array))
            print(min(read_array))
            #PWelch ########################################################
            #f_avg, m0, 01
            f_avg=eng.func_Pwelch(read_array)
            percen=np.percentile(read_array, 90)
            # Append rows ########################################################
            #df = df.append({'Zaber_pos':f_avg[0][0], 'F_avg':f_avg[0][0], 'M0':f_avg[0][1], 'M1':f_avg[0][2]},ignore_index = True)
            posZab=device_list[2].get_position()
            df = pd.concat([df, pd.DataFrame.from_records([{'Zaber_pos':posZab,'Percen':percen, 'F_avg':f_avg[0][0], 'M1':f_avg[0][1], 'M0':f_avg[0][2], 'F_avg_noise':f_avg[0][3], 'M1_noise':f_avg[0][4], 'M0_noise':f_avg[0][5]}])], ignore_index=True)
            
            counter=counter+1

        df.to_csv('Calibration_Zaber_0.csv')  

        