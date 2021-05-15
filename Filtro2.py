import scipy
import sys  
from scipy import signal
from scipy import pi
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
import numpy as np    
from scipy.signal import butter, lfilter, freqz, filtfilt
import csv
import pandas as pd
import numpy as np

def plot():
    data = pd.read_csv(r"C:\Users\Asus\Documents\GitHub\Tesis\ServicioFlask\Recursos\User1SerCsvMaSolo.csv")
    # sensor_data = data[['data']]
    print(data)
    
    # sensor_data = np.array(data)
    sensor_data = data
    
    print(sensor_data)
    plt.plot(sensor_data)
    plt.show()

    filtered_signal = bandPassFilter(sensor_data)

    print(sensor_data)
    plt.plot(filtered_signal)
    plt.show()

def bandPassFilter(signal):

    fs=4000.0
    lowcut = 0.50
    highcut = 45.00

    nyq = 0.5 * fs
    low = lowcut/nyq
    high = highcut/nyq

    order = 2

    b,a= butter(order, [low,high], 'bandpass', analog=False)

    y = filtfilt(b, a, signal, axis=0)

    return(y)

plot()