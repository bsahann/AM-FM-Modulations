import sounddevice as sd
import asyncio
from rtlsdr import RtlSdr
import nest_asyncio
import sys
import numpy as np
from scipy.signal import lfilter, decimate,butter
import matplotlib.pylab as plt
import numpy as np
from scipy import signal



interrupt = False
mono_signal: int = 15000 #part of the signal that interests us
fm_bandwidth: int = 220500
nest_asyncio.apply()


#decimate to lower sample 
def decimation(samples, factor):
    return decimate(samples, factor)
def offset(samples, freq_offset: float, freq_sr):
    t = np.arange(len(samples)) / freq_sr
    return samples * np.exp(-1.0j * 2.0 * np.pi * freq_offset * t)

#Functions needed for filtering
def lowpass(data, cutoff, sr, order = 5):
    x  = 0.5 * sr
    normal_cutoff = cutoff / x
    arg1, arg2 = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered = signal.lfilter(arg1, arg2, data)
    return filtered

#demodulation
def demodulation(samples):
    angle = np.angle(samples)
    correct_angle = np.unwrap(angle)#unwrap allows us to find phase
    demod = np.diff(correct_angle)
    return demod
    


# Going one by one trough steps and decimation to soundkart
def audio_mono(samples, sampling_rate, offs):
    samples = offset(samples, offs, sampling_rate)
    samples = decimation(samples, int(sampling_rate // fm_bandwidth))
    samples = demodulation(samples)
    samples = lowpass(samples,mono_signal+4000,fm_bandwidth)
    samples = decimation(samples, int(fm_bandwidth // 44100))
    return samples

#using buffers , writing in buffer
async def sdr_streaming(audioqueue,center_freq,blocksize,sdr):
    offs = 200000
    
    # sdr configure
    center_frequency = center_freq
    sdr.sample_rate = 1102500
    sdr.center_freq = center_frequency - 200000
    sdr.gain = "auto"
    
    async for samples in sdr.stream(blocksize):#using samples

        await audioqueue.put(audio_mono(samples, sdr.sample_rate,offs ))#put processed data in buffer
    

#soundkart reading of buffer
async def read_and_play(freq, blocksize,sdr,audioqueue):
    
    def callback(outdata, frames, time, status):#1st thread write in buffer 
        try:#data written
            data = audioqueue.get_nowait()
            outdata[:, 0] = data
            audioqueue.task_done()#Indicate that a formerly enqueued task is complete
        except asyncio.QueueEmpty:  #error
            outdata.fill(0)
        except ValueError:  #error
            outdata.fill(0)
            outdata[: data.size, 0] = data
        

    with sd.OutputStream(#2nd thread soundkart reading from buffer
            samplerate=44100,
            blocksize=int(blocksize/25),
            channels=1,
            callback=callback,
    ):
        await sdr_streaming( audioqueue, freq, blocksize,sdr)
    
        


sdr = RtlSdr()
audioqueue: asyncio.Queue(np.ndarray) = asyncio.Queue()
try:   
    asyncio.run(read_and_play( 98.4e6, 2400000,sdr,audioqueue))#loop till task is done
    
    
    
 #Closing sdr after being done   
except KeyboardInterrupt:
    try:
        interrupt=True
    except:
        pass
    try:
        asyncio.run(audioqueue.join())
    except:
        pass
finally:
    try:
        sdr.close()
    except:
        pass
    sys.exit('')

