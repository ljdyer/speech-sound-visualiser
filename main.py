
# TODO put each section into a separate function 

# Adapted from the following sources:
# https://medium.com/analytics-vidhya/understanding-the-mel-spectrogram-fca2afa2ce53
# https://stackoverflow.com/a/43347984/17568469

import math
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

MY_FILE = "comp_ling_fun.wav"

# ==============================================================================

# Get the audio time series and sample rate from the .wav file
sound_data, sample_rate = librosa.load(MY_FILE)

# Display sampling rate
print(sample_rate)

# Quantize to 8-bit audio (convert amplitude measures to integers between -128
# and 127)
sound_data_quantized = librosa.mu_compress(sound_data, quantize=True)

sample_points = len(sound_data)                         # Number of sample points
signal_length = sample_points / sample_rate             # Length of sound file in seconds
point_duration = signal_length * 1000 / sample_points   # Duration of an sample point
                                                        # in ms

# Generate list of time points (in ms) to display on x axis
time_points = [ x / sample_rate * 1000 for x in range(sample_points)]

# Plot
quantized_title = f"Your {round(signal_length, 3)}s audio recording quantized " + \
                  "as 8-bit integer values"
plt.plot(time_points, sound_data)
plt.title(quantized_title)
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.show()

# ==============================================================================

"""Get spectrum for a windowed segment by converting the signal from the time
domain into the frequency domain by Fourier transform

From http://librosa.org/doc/main/generated/librosa.stft.html: Short-time
Fourier transform (STFT). The STFT represents a signal in the time-frequency
domain by computing discrete Fourier transforms (DFT) over short overlapping
windows."""

# n_fft is length of windowed signal after padding with zeroes. Librosa
# recommends n_fft=512 for speech processing, which corresponds to 23
# miliseconds at a sample rate of 22050 Hz (the default target sample rate for
# librosa.load).

n_fft = 512
fft_start = math.floor(sample_points / 2)   # Start in the middle to maximise
                                            # chance of catching some speech
fft_end = fft_start + n_fft

# Get duration and position to display to user

def ms_to_sec_display(ms: float) -> str:
    """Convert time in miliseconds to string in format mm:ss.sss"""

    s = round(ms/1000, 3)
    m, s = divmod(s, 60)
    before_dp, after_dp = divmod(s, 1)
    mins = str(int(m)).zfill(2)
    secs_before_dp = str(int(before_dp)).zfill(2)
    secs_after_dp = str(after_dp)[2:5]
    return f'{mins}:{secs_before_dp}.{secs_after_dp}'

time_start = time_points[fft_start]
time_end = time_points[fft_end]
duration = round(time_end - time_start)

# Get spectrum
spectrum = np.abs(librosa.stft(sound_data[fft_start:fft_end],
                               n_fft=n_fft, hop_length = n_fft+1))

# Plot
spectrum_title = f"Spectrum of the {duration}ms window of audio at " + \
                 f"{ms_to_sec_display(time_start)}-{ms_to_sec_display(time_end)}"
# plt.plot(spectrum)
# plt.title(spectrum_title)
# plt.xlabel('Frequency bin')
# plt.ylabel('Amplitude')
# plt.show()


# ==============================================================================

# Compute spectrogram
spec = np.abs(librosa.stft(sound_data, hop_length=512))

# Convert colour dimension to decibels (essentially log scale of amplitude)
spec = librosa.amplitude_to_db(spec, ref=np.max)

# Plot
librosa.display.specshow(spec, sr=sample_rate, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram of your audio recording')
plt.show()
# TODO work out why time is different