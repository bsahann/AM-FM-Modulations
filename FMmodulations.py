import matplotlib.pylab as plt
import numpy as np
from scipy import signal
##Functions needed
#frequency domain functions
def functionfrequencydomain(data):
    x = np.fft.fftshift(np.fft.fft(data))#np.fft.fftshift makes the 0 component shift to center,np.fft.fft is fourier transform
    return np.abs(x)#a+ib-> x(sqrt a^2+b^2)

def spectrumrange(spectrum,spectrumRange):
    return spectrum[int(len(spectrum)/2) - spectrumRange:int(len(spectrum)/2) + spectrumRange]

def frequencyrange(spectrumRange):
    return np.arange(-spectrumRange/2, spectrumRange/2, 0.5)
#Functions needed for filtering
def lowpass(data, cutoff, sr, order = 5):
    x  = 0.5 * sr
    normal_cutoff = cutoff / x
    arg1, arg2 = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered = signal.lfilter(arg1, arg2, data)
    return filtered
def demodulation(samples):
    angle = np.angle(samples)
    correct_angle = np.unwrap(angle)#unwrap allows us to find phase
    demod = np.diff(correct_angle)
    return demod
fig, ax = plt.subplots(5,2)
#Time between sampling
t = 0.0001

ts = plt.arange(0,2,t)
sr = 1/t #sample rate
freqsignal = 1.0
ysignal= plt.sin(2.0 * plt.pi * freqsignal * ts)
intgysignal = -plt.cos(2.0 * plt.pi * freqsignal * ts) / 2.0 * plt.pi

#Carrier 
fc = 100
yc = plt.sin(2.0 * plt.pi * fc * ts)

modfactor = 5
ymodulated = plt.cos(2.0 * plt.pi * fc * ts + 2.0 * plt.pi * modfactor * intgysignal)

 
#calculate spectrum of ysignal
spectrumRange = 250 # Hz
freqrange = frequencyrange(spectrumRange)
spectrumy = functionfrequencydomain(ysignal)
spectrumyrange = spectrumrange(spectrumy,spectrumRange)

#plot ysignal
ax[0,0].plot(ts, ysignal)
ax[0,0].set_ylabel("Signal", fontsize = 8)
ax[0,0].set_title("Time(s)", fontsize = 20)
ax[0,1].plot(freqrange,spectrumyrange)
ax[0,1].set_title("Frequency(Hz)", fontsize = 20)


#calculate spectrum of ymodulated
spectrumRange = 500
freqrange = frequencyrange(spectrumRange)
spectrumymodulated = functionfrequencydomain(ymodulated)
spectrumy_modulatedrange = spectrumrange(spectrumymodulated,spectrumRange)

#plot ymodulated
ax[1,0].plot(ts,ymodulated)
ax[1,0].set_ylabel("modulation", fontsize = 8)
ax[1,1].plot(freqrange,spectrumy_modulatedrange)

#calculate I and Q components,sin and cos apart so 90 degree phase called quadrature
#Amplitude*angle of quadrature
I = ymodulated*np.sin(2*np.pi*fc*ts)
Q = ymodulated*np.cos(2*np.pi*fc*ts)



#calculate filtered I and Q signals 
Ifiltered = lowpass(I, 40, sr)
Qfiltered = lowpass(Q, 40, sr)

Ifiltered_spectrum = functionfrequencydomain(Ifiltered)
Qfiltered_spectrum = functionfrequencydomain(Qfiltered)
spectrumRange = 250
freqrange = frequencyrange(spectrumRange)
Ifiltered_spectrum_range = spectrumrange(Ifiltered_spectrum,spectrumRange)
Qfiltered_spectrum_range = spectrumrange(Qfiltered_spectrum,spectrumRange)


#plot filtered I and Q signals and spectra
ax[2,0].plot(ts, Ifiltered)
ax[2,0].set_ylabel("I filtered", fontsize = 8)
ax[2,1].plot(freqrange, Ifiltered_spectrum_range)
ax[3,0].plot(ts, Qfiltered)
ax[3,0].set_ylabel("Q filtered", fontsize = 8)
ax[3,1].plot(freqrange, Qfiltered_spectrum_range)


#demodulation + filtering to get original signal
IQsignal = I + 1j*Q
demodulated_signal = demodulation(IQsignal)
filtered_signal = lowpass(demodulated_signal, 20, sr)

#spectrum of demodulated signal
spectrumRange = 350 
freqrange = frequencyrange(spectrumRange)
fsignal = functionfrequencydomain(filtered_signal)
fsignalrange = spectrumrange(fsignal,spectrumRange)

#plot demodulated signal
ax[4,0].plot(ts[1:], filtered_signal)
ax[4,0].set_ylabel("demodulation", fontsize = 8)
ax[4,1].plot(freqrange, fsignalrange)
