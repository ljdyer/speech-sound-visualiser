
# TODO put each section into a separate function 

# Adapted from the following sources:
# https://medium.com/analytics-vidhya/understanding-the-mel-spectrogram-fca2afa2ce53
# https://towardsdatascience.com/getting-to-know-the-mel-spectrogram-31bca3e2d9d0
# https://stackoverflow.com/a/43347984/17568469
# https://stackoverflow.com/questions/67451239/log-mel-spectrogram-using-librosa

import math
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

WAVEFORM_FILENAME = 'static/images/waveform.png'
SPECTRUM_FILENAME = 'static/images/spectrum.png'
SPECTROGRAM_FILENAME = 'static/images/spectrogram.png'
MEL_SPECTROGRAM_FILENAME = 'static/images/mel_spectrogram.png'

MY_FILE = "comp_ling_fun.wav"


# ====================
def ms_to_sec_display(ms: float) -> str:
    """Convert time in miliseconds to string in format mm:ss.sss"""

    s = round(ms/1000, 3)
    m, s = divmod(s, 60)
    before_dp, after_dp = divmod(s, 1)
    mins = str(int(m)).zfill(2)
    secs_before_dp = str(int(before_dp)).zfill(2)
    secs_after_dp = str(after_dp)[2:5]
    return f'{mins}:{secs_before_dp}.{secs_after_dp}'


# ====================
def save_matplotlib_plot(*args, title: list, xlabel: str, ylabel: str,
                         filename: str):
    """Save a matplotlib plot"""

    plt.plot(*args)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(filename)
    plt.close()


# ====================
def save_librosa_specshow(*args, sr: int, title: str, 
                          x_axis: str=None, y_axis: str=None,
                          filename: str):
    """Save a librosa specshow"""

    librosa.display.specshow(*args, sr=sr, y_axis=y_axis, x_axis=x_axis)
    plt.title(title)
    plt.colorbar(format='%+2.0f dB')
    plt.savefig(filename)
    plt.close()


# ====================
def save_plots(filename: str):
    """Given an audio file, save plots of the following:
    
    Raw waveform: waveform.png
    Spectrum for single frame: spectrum.png
    Spectrogram: spectrogram.png
    Mel spectrogram: mel_spectrogram.png"""

    # === Raw waveform ===

    # Get the audio time series and sample rate from the .wav file
    sound_data, sample_rate = librosa.load(filename)

    # Quantize to 8-bit audio (convert amplitude measures to integers between
    # -128 and 127)
    sound_data_quantized = librosa.mu_compress(sound_data, quantize=True)

    # Number of sample points
    num_points = len(sound_data_quantized)
    # Length of sound file in seconds
    signal_length = num_points / sample_rate 

    # Generate list of time points (in ms) to display on x axis
    time_points = [ x / sample_rate * 1000 for x in range(num_points)]

    # Save plot
    waveform_title = f"Your {round(signal_length, 3)}s audio recording quantized " + \
                    f"as 8-bit integer values (sampling rate: {sample_rate}Hz)"
    save_matplotlib_plot(time_points, sound_data_quantized,
                         xlabel='Time (ms)', ylabel='Amplitude',
                         title=waveform_title, filename=WAVEFORM_FILENAME)


    # === Spectrum ===

    # """Get spectrum for a windowed segment by converting the signal from the
    # time domain into the frequency domain by Fourier transform

    # From http://librosa.org/doc/main/generated/librosa.stft.html:
    # Short-time Fourier transform (STFT).
    # The STFT represents a signal in the time-frequency domain by computing
    # discrete Fourier transforms (DFT) over short overlapping windows.""""

    # # n_fft is length of windowed signal after padding with zeroes. Librosa
    # # recommends n_fft=512 for speech processing, which corresponds to 23
    # # miliseconds at a sample rate of 22050 Hz (the default target sample rate for
    # # librosa.load).

    sound_data, sample_rate = librosa.load(filename)
    num_points = len(sound_data)
    time_points = [ x / sample_rate * 1000 for x in range(num_points)]
    n_fft = 512
    # Choose a frame in the middle of the audio file to maximise the chance that
    # it corresponds to speech
    fft_start = math.floor(num_points / 2)
    fft_end = fft_start + n_fft

    # Get duration and position to display to user
    time_start = time_points[fft_start]
    time_end = time_points[fft_end]
    duration = round(time_end - time_start)

    
    # Get spectrum
    spectrum = np.abs(librosa.stft(sound_data[fft_start:fft_end],
                                n_fft=n_fft, hop_length = n_fft+1))

    # *** Save plot of spectrum ***
    spectrum_title = f"Spectrum of the {duration}ms window of audio at " + \
                    f"{ms_to_sec_display(time_start)}-{ms_to_sec_display(time_end)}"
    save_matplotlib_plot(spectrum, xlabel='Frequency bin', ylabel='Amplitude',
                         title=spectrum_title, filename=SPECTRUM_FILENAME)


    # # === Spectrogram ===

    # Compute spectrogram
    spectrogram = np.abs(librosa.stft(sound_data, hop_length=512))
    # Convert colour dimension to decibels (essentially log scale of amplitude)
    spectrogram = librosa.amplitude_to_db(spectrogram, ref=np.max)

    # **** Save plot of spectrogram ***

    spectrogram_title = 'Spectrogram of your audio recording'
    save_librosa_specshow(spectrogram, sr=sample_rate, x_axis='time', y_axis='log',
                          title=spectrogram_title, filename=SPECTROGRAM_FILENAME)


    # === Mel spectrogram ===

    # From http://practicalcryptography.com/miscellaneous/machine-learning
    # /guide-mel-frequency-cepstral-coefficients-mfccs/:
    # In this section the example will use 10 filterbanks because it is easier
    # to display, in reality you would use 26-40 filterbanks.
    # To get the filterbanks shown in figure 1(a) we first have to choose a
    # lower and upper frequency. Good values are 300Hz for the lower and
    # 8000Hz for the upper frequency.

    # Compute mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=sound_data,
                                                    sr=sample_rate,
                                                    n_fft=512,
                                                    n_mels=32,
                                                    fmax=8000,
                                                    fmin=300)
    # Convert colour dimension to decibels (essentially log scale of amplitude)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

    # Save plot
    mel_spectrogram_title = 'Mel spectrogram of your audio recording with n_mels=32'
    save_librosa_specshow(mel_spectrogram, sr=sample_rate, x_axis='time', 
                          title=mel_spectrogram_title,
                          filename=MEL_SPECTROGRAM_FILENAME)

    
# ====================
if __name__ == "__main__":

    save_plots(MY_FILE)