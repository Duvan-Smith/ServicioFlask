# import scipy
# import sys  
# from scipy import signal
# from scipy import pi
# from scipy.io.wavfile import write
# import matplotlib.pyplot as plt
# import numpy as np    
# from scipy.signal import butter, lfilter, freqz   


# # ----- ----- ----- -----    
# def butter_highpass(cutoff, fs, order=5):
#     nyq = 0.5 * fs
#     normal_cutoff = cutoff / nyq
#     b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
#     return b, a

# def butter_highpass_filter(data, cutoff, fs, order=5):
#     b, a = butter_highpass(cutoff, fs, order=order)
#     y = signal.filtfilt(b, a, data)
#     return y


# # ----- -----    
# # (1)
# def foo(sel):
#     if (sel == 1):
#         # Filter requirements.
#         order = 6
#         fs = 300.0  # sample rate, Hz
#         cutoff = 10  # desired cutoff frequency of the filter, Hz

#         # Get the filter coefficients so we can check its frequency response.
#         b, a = butter_highpass(cutoff, fs, order)

#         # Plot the frequency response.
#         w, h = freqz(b, a, worN=8000)
#         plt.subplot(2, 1, 1)
#         plt.plot(0.5 * fs * w / np.pi, np.abs(h), 'b')
#         plt.plot(cutoff, 0.5 * np.sqrt(2), 'ko')
#         plt.axvline(cutoff, color='k')
#         plt.xlim(0, 0.5 * fs)
#         plt.title("High Filter Frequency Response")
#         plt.xlabel('Frequency [Hz]')
#         plt.grid()

#         # Demonstrate the use of the filter.
#         # First make some data to be filtered.
#         T = 0.5  # seconds
#         n = int(T * fs)  # total number of samples
#         t = np.linspace(0, T, n, endpoint=False)
#         # "Noisy" data.  We want to recover the 20 Hz signal from this.
#         data = np.sin(1.2 * 2 * np.pi * t) + 1.5 * np.cos(5 * 2 * np.pi * t) + 0.5 * np.sin(20.0 * 2 * np.pi * t)
#         print(data)
#         # Filter the data, and plot both the original and filtered signals.
#         y = butter_highpass_filter(data, cutoff, fs, order)

#         plt.subplot(2, 1, 2)
#         plt.plot(t, data, 'b-', label='data')
#         plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
#         plt.xlabel('Time [sec]')
#         plt.grid()
#         plt.legend()

#         plt.subplots_adjust(hspace=0.35)
#         plt.show()
#     else:
#         print ('Please, choose among choices, thanks.')


# # ----- -----
# def main():
#     sel = 1
#     foo(sel)


# # ----- ----- ----- ----- ----- -----
# if __name__ == '__main__':
#     main()

import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
def sine_generator(fs, sinefreq, duration):
    T = duration
    nsamples = fs * T
    w = 2. * np.pi * sinefreq
    t_sine = np.linspace(0, T, nsamples, endpoint=False)
    y_sine = np.sin(w * t_sine)
    result = pd.DataFrame({ 
        'data' : y_sine} ,index=t_sine)
    return result

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

fps = 30
sine_fq = 100 #Hz
duration = 10 #seconds
sine_5Hz = sine_generator(fps,sine_fq,duration)
print(sine_5Hz)
print()
sine_fq = 1 #Hz
duration = 10 #seconds
sine_1Hz = sine_generator(fps,sine_fq,duration)
print(sine_1Hz)
print()

sine = sine_5Hz + sine_1Hz
print(sine)
print()
print(sine.data)
print()

filtered_sine = butter_highpass_filter(sine.data,10,fps)
print(filtered_sine)
print()

plt.figure(figsize=(20,10))
plt.subplot(211)
plt.plot(range(len(sine)),sine)
plt.title('generated signal')
plt.subplot(212)
plt.plot(range(len(filtered_sine)),filtered_sine)
plt.title('filtered signal')
plt.show()


# from scipy.signal import butter, lfilter


# def butter_bandpass(lowcut, highcut, fs, order=5):
#     nyq = 0.5 * fs
#     low = lowcut / nyq
#     high = highcut / nyq
#     b, a = butter(order, [low, high], btype='band')
#     return b, a


# def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
#     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
#     y = lfilter(b, a, data)
#     return y


# if "__main__"== "__main__":
#     import numpy as np
#     import matplotlib.pyplot as plt
#     from scipy.signal import freqz

#     # Sample rate and desired cutoff frequencies (in Hz).
#     fs = 5000.0
#     lowcut = 500.0
#     highcut = 1250.0

#     # Plot the frequency response for a few different orders.
#     plt.figure(1)
#     plt.clf()
#     for order in [3, 6, 9]:
#         b, a = butter_bandpass(lowcut, highcut, fs, order=order)
#         w, h = freqz(b, a, worN=2000)
#         plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

#     plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
#              '--', label='sqrt(0.5)')
#     plt.xlabel('Frequency (Hz)')
#     plt.ylabel('Gain')
#     plt.grid(True)
#     plt.legend(loc='best')

#     # Filter a noisy signal.
#     T = 0.05
#     nsamples = T * fs
#     t = np.linspace(0, T, nsamples, endpoint=False)
#     a = 0.02
#     f0 = 600.0
#     x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
#     x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
#     x += a * np.cos(2 * np.pi * f0 * t + .11)
#     x += 0.03 * np.cos(2 * np.pi * 2000 * t)
#     plt.figure(2)
#     plt.clf()
#     plt.plot(t, x, label='Noisy signal')

#     y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
#     plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)
#     plt.xlabel('time (seconds)')
#     plt.hlines([-a, a], 0, T, linestyles='--')
#     plt.grid(True)
#     plt.axis('tight')
#     plt.legend(loc='upper left')

#     plt.show()
