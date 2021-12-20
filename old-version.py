
# Adapated from https://stackoverflow.com/a/43347984/17568469

import numpy
import matplotlib.pyplot as plt
import pylab
from scipy.io import wavfile
from scipy.fftpack import fft

MY_FILE = "LRMonoPhase4.wav"

# ==============================================================================

# Read file to get sampling frequency and array of sound data
sample_rate, sound_data = wavfile.read(MY_FILE)

# Scipy does not support 24 bit .wav files
sound_data_type = sound_data.dtype
if sound_data_type not in ['int16','int32']:
    raise ValueError(f'24 bit .wav files are not supported ({MY_FILE}).')

# Convert array of sound data to floating point values between -1 and 1.
sound_data = sound_data / (2.**15)
# Get number of data points in the sample
sample_points = float(sound_data.shape[0])
# Get duration of the sound file in seconds
signal_duration = sample_points / sample_rate
# If there are two channels, select left one only
left_channel_data = sound_data[:,0]


# === Plot raw waveform ===

# Create an array of sample points in one dimension
time_array = numpy.arange(0, sample_points, 1)
time_array = time_array / sample_rate
# Scale to milliSeconds
time_array = time_array * 1000
print(time_array)

# Plot amplitude against time
plt.plot(time_array, left_channel_data, color='green')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.show()


# === Plot frequency content ===

# Get frequency from amplitude and time using Fast Fourier Transform (FFT)
# algorithm to compute the discrete Fourier transform (DFT).
# https://en.wikipedia.org/wiki/Fast_Fourier_transform

# Get the length of the sound_data object array
sound_data_length = len(sound_data)
# Get the Fourier transformation of each sample point
fft_array = fft(sound_data)
fft_array = fft(left_channel_data)
# Get the number of unique points
num_unique_points = int(numpy.ceil((sound_data_length + 1) / 2.0))
print(num_unique_points)
fft_array = fft_array[0:num_unique_points]

# FFT contains both magnitude and phase, given in complex numbers in
# real + imaginary parts (a + ib).
# Take the absolute value to get only the real part.
fft_array = abs(fft_array)

# Scale fft array by number of sample points so that magnitude does not
# depend on length of signal or sample rate
fft_array = fft_array / float(sound_data_length)
# FFT has both positive and negative information. Square to get positive only
fft_array = fft_array **2

if sound_data_length % 2 > 0:
    # Odd number of points in FFT
    fft_array[1 : len(fft_array)] = fft_array[1 : len(fft_array)] * 2
else:
    # Even number of points in FFT
    fft_array[1 : len(fft_array) - 1] = fft_array[1 : len(fft_array) - 1] * 2

freq_array = numpy.arange(0, num_unique_points, 1.0) \
                * (sample_rate / sound_data_length)

# Plot the frequency
plt.plot(freq_array / 1000, 10 * numpy.log10(fft_array), color='blue')
plt.xlabel('Frequency (Khz)')
plt.ylabel('Power (dB)')
plt.show()


# === Plot spectrogram ===