import numpy as np
from scipy.signal import butter, lfilter
from utils import *

# Butterworth bandpass filter function
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a


# Function to apply the bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data, axis=0)
    return y


# Example function to filter into different frequency bands
def filter_eeg_bands(eeg_data, fs):
    bands = {
        'Delta': (0.5, 4),
        'Theta': (4, 8),
        'Alpha': (8, 12),
        'Beta': (12, 30),
        'Gamma': (30, 45)
    }

    filtered_data = {}

    for band, (low, high) in bands.items():
        filtered_data[band] = bandpass_filter(eeg_data, low, high, fs)

    return filtered_data


stream_list = show_xdf_data("%r")

str_1 = stream_list[0]
str_2 = stream_list[1]

time_1 = str_1[0]
time_2 = str_2[0]

print("Timestamps of stream 1: ", time_1, f"\n Length: {time_1.shape}")
print("Timestamps of stream 2: ", time_2, f"\n Length: {time_2.shape}")