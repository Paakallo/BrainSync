import numpy as np
from scipy.signal import butter, lfilter


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




fs = 256  # Hz
n_samples = 1000
n_channels = 14

eeg_data = np.random.randn(n_samples, n_channels)


filtered_eeg = filter_eeg_bands(eeg_data, fs)


for band, data in filtered_eeg.items():
    print(f"{band} band filtered data shape: {data.shape}")
