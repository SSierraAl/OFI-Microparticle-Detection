from LibrariesImport import *

#Filtro butter bandpass  ############################################################
def butter_bandpass_filter(data, lowcut, highcut, order,fs):
    nyquist = 0.5 * fs
    lowcut = lowcut / nyquist
    highcut = highcut / nyquist
    b, a = butter(order, [lowcut, highcut], btype='band', analog=False)
    y = filtfilt(b, a, data)
    return y



#FFT ###############################################################################
def FFT_calc(datos, samplefreq):
    n = len(datos)
    #Hamming window
    #window = np.hamming(n)  # Aplica la ventana de Hamming a los datos
    #datos_windowed = datos * window
    fft_result = np.fft.rfft(datos)
    freq_fft = np.fft.rfftfreq(len(datos), 1 / samplefreq)
    amplitude = np.abs(fft_result)
    phase = np.angle(fft_result)
    #Delete first data
    #amplitude = amplitude[50:]
    #freq_fft = freq_fft[50:]

    #Soft Frequency
    #window_size = 5
    #window = np.ones(window_size) / window_size
    #amplitude = np.convolve(amplitude, window, mode='valid')
    #freq_fft = np.convolve(freq_fft, window, mode='valid')
    

    return amplitude, freq_fft, phase


#Welch ###############################################################################
def Welch_calc(datos, samplefreq):
    n = len(datos)
    #Hamming window
    #window = np.hamming(n)  # Aplica la ventana de Hamming a los datos
    #datos_windowed = datos * window
    
    #freq, amplitude =signal.welch(datos, fs=samplefreq, nperseg=n/10)
    freq, amplitude =signal.welch(datos, fs=samplefreq)
    # Convert PSD to dB scale
    amplitude = 10 * np.log10(amplitude)
    return freq , amplitude


#FWHW ###############################################################################
def get_full_width(x: np.ndarray, y: np.ndarray, height: float = 0.5) -> float:
    height_half_max = np.max(y) * height
    index_max = np.argmax(y)
    x_low = np.interp(height_half_max, y[:index_max+1], x[:index_max+1])
    x_high = np.interp(height_half_max, np.flip(y[index_max:]), np.flip(x[index_max:]))

    return x_high, x_low


#Gaussian Fit ##############################################################################
def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-(x - mean)**2 / (2 * stddev**2))



# Particle Detection by algorithm ############################################
def search_particle(wavelet, umbral, n_puntos_consecutivos, inicio):

    #Counter
    Iteration=0
    #Set condition
    check_condition=False
    #Create a vector with True and False for analysis
    supera_umbral = wavelet > umbral
    supera_umbral_2 = wavelet < -umbral
    supera_umbral= supera_umbral | supera_umbral_2
    #Create a vector to know when finish the particle
    no_supera_umbral = ~supera_umbral

    fin=len(wavelet)
    while check_condition==False:
        # Aplicar una ventana deslizante para encontrar el segmento
        for i in range(inicio,len(wavelet) - n_puntos_consecutivos + 1):
            if all(supera_umbral[i:i + n_puntos_consecutivos]):
                inicio = i
                break
        for j in range(inicio, len(wavelet)):
            if all(no_supera_umbral[j:j + n_puntos_consecutivos]):
                #inicio = i
                fin = j+n_puntos_consecutivos
                break
        inicio_segmento=inicio
        fin_segmento=fin  
        # check condition
        if ( (inicio_segmento < np.argmax(wavelet) and fin_segmento > np.argmax(wavelet)) or (inicio_segmento < np.argmin(wavelet) and fin_segmento > np.argmin(wavelet))):
            check_condition=True
        else:
            Iteration=Iteration+1
            inicio=fin_segmento

        if(Iteration >100):
            inicio=0
            fin=len(wavelet)
            check_condition=True
            print(Iteration)
            print('Particle not detected')

    print('Particle detected in iteration: '+ str(Iteration))
    
    if inicio>n_puntos_consecutivos:
        inicio=inicio-n_puntos_consecutivos
    
    return inicio, fin


# Simulate Particle ###########################################



def simulated_particle(P_size, Speed_Mode, P_Speed, P_Freq_Freq,P_Freq_amplitud, Inc_Angle, Laser_Lambda, Po, T_impact, Num_Particles, Time_max, Adq_Freq ):
    """
        simulated_particle create a signal of an individual particle

        Parameters
        -----------
        param P_size         : Diameter of the particles [m]
        param Speed_Mode     : True if the speed of p. is known
        param P_Speed        : Particle Speed [m/s]
        param P_Freq_Freq    : Particle Frequency [Hz] [np vector]
        param P_Freq_amplitud: Particle Amplitud [np vector] 
        param Inc_Angle      : Incident Angle [degrees]
        param Laser_Lambda   : Laser wavelegth [m]
        param Po             : Power of the Standalone Laser [mV]
        param T_impact       : Time in wihch the laser shoots perpendiculary onto particle center [ms]
        param Num_Particles  : Number of particles in the sensing volumen
        param Time_max       : For Time data vector
        param Adq_Freq       : Adquisiton Frequency[Hz]

        Returns
        -----------
        return P_t, t        : Time vector of the particle, Time vector
    """
    #Creating time vector for the singal
    t = np.linspace(0, Time_max, Time_max)
    # Vector to analyze multiple particles
    sumatoria = np.zeros_like(t)
    
    if Speed_Mode==True:
        #Dopler frequency ----------------- The particle velocity is known
        #|fd| = 2*V[m/s]*sen(theta)/lambda
        f = abs(2 * P_Speed * np.sin(Inc_Angle) / Laser_Lambda)
        #print('----Frequency check Func----')
        #print(f)
        #print('----------')


        #print('---P_speed check---')
        #P_speed=((f*Laser_Lambda)/(abs(np.sin(Inc_Angle))*2))
        #print(P_speed)
        #print('----------')
        
        ###############################
        #Adjusting the sample frequency
        f=f/Adq_Freq

    else:
        # Doppler frequency ---------------- The Frequency spectrum of the data is known
        f=P_Freq_Freq[np.argmax(P_Freq_amplitud)]
        #print('----Frequency check Func----')
        #print(f)
        #print('----------')
    

        ###############################
        #Adjusting the sample frequency
        f=f/Adq_Freq

        #print('---P_speed check---')
        P_Speed=((f*Laser_Lambda)/(abs(np.sin(Inc_Angle))*2))
        #print(P_Speed)
        #print('----------')

        

    # Translation time period of the particle proportional to (Diameter/Speed)
    #Control the amplitud of the envelop
    #Diameter of the particles[m]
    b = P_size/  ((f*Laser_Lambda)/(abs(np.sin(Inc_Angle))*2))
    #Adjusting the amplitud 
    b=b*2

    # In case of multiple particles define the modulation index and the range of frequencies
    m_values = np.random.uniform(10, 15, Num_Particles)  # Valores de m aleatorios
    f_values = np.random.uniform(f, f*1.2, Num_Particles)  # Valores de f aleatorios

    # Calcular la suma de las componentes sinusoidales
    if Num_Particles == 1:
        sumatoria = 10 * np.cos(2 * np.pi * f*t-20)
    else:
        for i in range(Num_Particles):
            sumatoria += m_values[i] * np.cos(2 * np.pi * f_values[i]*t-20)

    # Calcular la función P(t)
    P_t = Po * (1 + sumatoria) * np.exp(-((t - T_impact)**2) / (2 * b**2))


    return P_t, t