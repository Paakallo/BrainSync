import matplotlib.pyplot as plt
import numpy as np
# from analysis.utils import read_raw_xdf
import pyxdf
import mne
from scipy.signal import welch
from utils import *


bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 12),
            'beta' : (13, 30),
            'low_gamma': (30, 45),
            'high_gamma': (55, 100)
        }

streams, header = pyxdf.load_xdf("453.xdf")
sfreq = float(streams[0]["info"]["nominal_srate"][0])

stream_list: list[np.array] = []
for stream in streams:
    if stream['info']['type'][0].lower() != 'eeg': # temp fix
        continue
    data = np.array(stream["time_series"]).T # shape (n_channels, n_times)
    data = remove_empty_channels(data)
    if np.all(data==0):
        continue
    stream_list.append(data)

win_size:int = round(5*sfreq) # seconds

all_list = [] # all_list -> streams -> channels -> sequences
print("Streams:", len(stream_list))
for stream in stream_list:
    stream_psd = [] # a list containing channels containing psd sequences
    n_channels, _ = stream.shape
    print("Stream: ", stream, '\n')
    
    for channel in range(n_channels):
        print("Channel: ", channel, '\n')
        ch_seq = []
        data:np.array = stream[channel]
        if (np.all(data==0)): continue # skip zero arrays
        n_samples:tuple = data.shape

        for i in range(n_samples[0]):
            if i+win_size == n_samples[0]: # if over last index
                win_size-=1
            seq = data[i:i+win_size]
            psd = welch(seq, fs=sfreq) # UserWarnings may concern zero arrays in first stream
            ch_seq.append(psd)

        ch_psd = channel_psd(ch_seq, bands)
        # ch_psd = ch_seq
        stream_psd.append(ch_psd)

    all_list.append(stream_psd)
