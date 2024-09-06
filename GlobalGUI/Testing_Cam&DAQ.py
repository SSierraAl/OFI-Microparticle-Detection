# Import necessary libraries from both files
from nidaqmx.stream_readers import AnalogSingleChannelReader
import nidaqmx as ni
from nidaqmx import constants
import numpy as np
import time
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from Camera_Selector_Fn import camera_selector
from pyphantom import Phantom, utils, cine
from collections import deque
import cv2
import os
import keyboard
from scipy.signal import butter, filtfilt

# Parameters for the DAQ
Laser_frequency = 500000  # Laser frequency in Hz
number_of_samples = 4096  # Number of samples for the DAQ (0.5s duration)
threshold = 0.03  # Define an example threshold for the FFT peak condition

# Camera initialization
ph = Phantom()  # Make a Phantom object
cam_count = ph.camera_count  # Check if a camera is around

cam = camera_selector(ph)  # Connect to specific camera
print("Connected to the existing camera")
cam = ph.Camera(0)

ph.discover(print_list=True)  # List available cameras

# Function to initialize camera parameters
def initialize_camera(cam):
    # Set camera parameters
    cam.resolution = (640, 128)  # Example resolution
    cam.exposure_time = 70  # Exposure time in microseconds
    cam.frame_rate = 8000  # Frame rate in frames per second
    cam.trigger_frames = 50
    cam.partition_count = 63  # Total number of partitions
    print("Camera parameters initialized.")

# Function to create Butterworth filter
def butter_filter(data, cutoff, fs, order, filter_type):
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq  # Normalize the cutoff frequency

    # Ensure the cutoff frequency is within the valid range
    if not (0 < normal_cutoff < 1):
        raise ValueError(f"Cutoff frequency {cutoff} is out of the valid range for the given sampling frequency {fs}.")

    # Generate Butterworth filter coefficients
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    # Apply the filter to the data using filtfilt for zero-phase filtering
    y = filtfilt(b, a, data)
    return y

# FFT calculation function
def FFT_calc(datos, samplefreq):
    n = len(datos)
    fft_result = np.fft.rfft(datos)
    freq_fft = np.fft.rfftfreq(len(datos), 1 / samplefreq)
    amplitude = np.abs(fft_result)
    phase = np.angle(fft_result)
    return amplitude, freq_fft, phase

# Function to start the DAQ and perform FFT analysis
def start_daq():
    DAQ_Data = np.zeros(number_of_samples, dtype=np.float64)
    with ni.Task() as task_Laser:
        # Signal Acquisition
        task_Laser.ai_channels.add_ai_voltage_chan("Dev2/ai0", max_val=5, min_val=-5)

        # Configure sampling clock with increased buffer size
        task_Laser.timing.cfg_samp_clk_timing(rate=Laser_frequency, 
                                              sample_mode=constants.AcquisitionType.CONTINUOUS,
                                              samps_per_chan=number_of_samples)
        # Initialize Stream reader
        reader = AnalogSingleChannelReader(task_Laser.in_stream)

        # Loop to handle multiple partitions
        for partition_number in range(1, cam.partition_count + 1):  # Iterate through all partitions
            print(f"Processing partition {partition_number}...")

            # Start recording in the specified partition
            cam.record(cine=partition_number, delete_all=True)  # Start recording for the current partition
            print(f"Recording started for partition {partition_number}.")

            # Acquire and process data
            while True:
                reader.read_many_sample(DAQ_Data, number_of_samples_per_channel=number_of_samples, timeout=10)
                DAQ_Data_2 = DAQ_Data.copy()

                # Apply Butterworth highpass and lowpass filters
                data_DAQ_highpass = butter_filter(DAQ_Data_2, 20000, Laser_frequency, 3, "high")
                data_DAQ_filtered = butter_filter(data_DAQ_highpass, 200000, Laser_frequency, 3, "low")

                # Perform FFT on the acquired signal
                amplitude, freq_fft, phase = FFT_calc(data_DAQ_filtered, Laser_frequency)

                # Debug: Print the maximum FFT magnitude
                print("Max FFT Magnitude:", np.max(amplitude))

                # Check if the peak exceeds the threshold
                if np.max(amplitude) > threshold:
                    # Save the DAQ data
                    daq_filename = f"daq_data_partition_{partition_number}_{time.time()}.npy"
                    np.save(daq_filename, DAQ_Data_2)
                    print(f"DAQ data saved as {daq_filename}")
                    break  # Exit the while loop to move to the next partition

            print(f"FFT peak detected, triggering camera for partition {partition_number}...")
            trigger_camera(partition_number)  # Trigger the camera for the current partition

# Function to trigger the camera and save the image
def trigger_camera(partition_number):
    print(f"Checking if the camera partition {partition_number} is recorded...")
    if not cam.partition_recorded(partition_number):
        cam.trigger()  # Trigger the camera to start recording for the current partition
        print(f"Camera triggered for partition {partition_number}.")
    else:
        print(f"Camera partition {partition_number} already recorded.")

    while not cam.partition_recorded(partition_number):
        time.sleep(0.1)  # Small delay to prevent busy waiting
    
    print(f"Recording completed for partition {partition_number}.")
    cine_obj = cam.Cine(partition_number)  # Make cine object for cine in RAM we just recorded

    # Read and display an image from the recorded cine
    print("Retrieving images from recorded cine...")
    test_range = utils.FrameRange(cine_obj.range.last_image - cam.trigger_frames, cine_obj.range.last_image)  # Set range
    image1 = cine_obj.get_images(test_range)  # Get images
    img = np.squeeze(image1)

    # Save the recording in a raw cine file (can be played in PCC application)
    print("Saving cine file to disk...")
    cine_obj.save(filename=os.path.expanduser('~') + f'/Desktop/Test/TestFile_Partition_{partition_number}', format=utils.FileTypeEnum(0), range=test_range)

    # Save the recording as a group of TIFF image files
    print("Saving TIFF images to disk...")
    cine_obj.save(filename=os.path.expanduser('~') + f'/Desktop/Test/TestFile_Partition_{partition_number}', format=utils.FileTypeEnum(-8), range=test_range)

# Main function to perform the combined process
def main():
    # Initialize camera parameters
    initialize_camera(cam)

    # Start the DAQ, perform FFT, and check triggering continuously
    print("Starting DAQ acquisition and monitoring...")
    start_daq()

    # After DAQ and camera recording is done, close camera and Phantom objects
    cam.close()  # Unregister camera objects
    ph.close()  # Unregister Phantom() objects
    print("Process completed for all partitions.")

if __name__ == "__main__":
    main()
