from time import sleep

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, get_window
from scipy.signal import butter,filtfilt

from numpy import trapz


folder_path = '.\DataEXP\BlueNew2'  # Replace with the path to your folder
number_of_samples=524288
vectors = [np.zeros(number_of_samples) for _ in range(15)]

acquisition_frequency = 1000000
Window = get_window('hamming', number_of_samples)


def butter_highpass_filter(data, cutoff, fs, order, text2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=text2, analog=False)
    y = filtfilt(b, a, data)
    return y

plt.close()
#plt.ion()
# Get a list of all .npy files in the folder
file_list = [f for f in os.listdir(folder_path) if f.endswith('.npy')]
# Sort the file list in ascending order
file_list.sort()
# Set the batch size to 14
batch_size = 10

maximaxi=0
minmin=99999999

#fig, (ax1, ax2) = plt.subplots(2,1, figsize=(15, 9))
fig, (ax2) = plt.subplots(1,1, figsize=(15, 9))
# Loop through the files in batches
for i in range(0, len(file_list), batch_size):
    # Get the current batch of file names
    batch_files = file_list[i:i+batch_size]
    
    CounterRMS=0
    for file_name in batch_files:
        file_path = os.path.join(folder_path, file_name)
        # Load and process the data from each file
        data = np.load(file_path)

        vectors[CounterRMS] = data
        CounterRMS=CounterRMS+1

    data=butter_highpass_filter(data, 100, acquisition_frequency, 3, "high")
    data=butter_highpass_filter(data, 40000, acquisition_frequency, 3, "low")
    FreqData=np.sqrt(np.mean(np.square(vectors), axis=0))

    frequencies, psd  = welch(data, fs=acquisition_frequency, window = Window)

    window_size = 15
    window = np.ones(window_size) / window_size
    frequencies = np.convolve(frequencies, window, mode='valid')
    psd = np.convolve(psd, window, mode='valid')

    if maximaxi< max(psd):
        maximaxi=max(psd)
    if minmin> min(psd):
        minmin=min(psd)


    #max min normalization x-xmin / xmax - x min
    #psd=(psd-4.3827080187108126e-21)/(0.008197344286034513-4.3827080187108126e-21)

    # Calculate the time array based on the acquisition frequency
    # Modify this value if your acquisition frequency is different
    time = np.arange(len(data)) / acquisition_frequency

    # Create a figure with two subplots
    




    m0 = abs(trapz(frequencies,psd)*1000)
    m1 = trapz(frequencies,frequencies*psd); #Calculate first moment
    f_avg=m1/m0
    m0=round(m0,3)
    f_avg=round(f_avg,3)
    #if True:
    if m0>1:  
        # Plot the PSD
        #ax2.semilogy(frequencies[:4000], psd[:4000],label=("batch: "+ str(i/14)+" f: "+ str(m0)))
        ax2.semilogy(frequencies[:4000], psd[:4000],label=("Pos: "+ str(int(i/14))+" f: "+ str(f_avg)))
        #ax2.semilogy(frequencies, psd)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Power Spectral Density')
        ax2.set_title('Power Spectral Density')

        # Plot the data over time
        #ax1.plot(time, data)
        #ax1.set_xlabel('Time (s)')
        #ax1.set_ylabel('Data')
        #ax1.set_title('Data over Time')

    # Adjust the spacing between subplots
    plt.tight_layout()

    # Display the figure
plt.legend(loc="upper right",fontsize=6)
plt.grid(visible=True)
plt.show()
    
    #plt.pause(2)
    #plt.close()
    #print("Batch number: " + str(i/14))

    
    
    