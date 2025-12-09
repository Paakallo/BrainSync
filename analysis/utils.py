from matplotlib import pyplot as plt
import numpy as np
import pyxdf
import mne
import os

bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 12),
            'beta' : (13, 30),
            'low_gamma': (30, 45),
            'high_gamma': (55, 100)
        }


def plot_eeg_data(df, part, file_index):
    """
    Plot the EEG data and save the plot as a PNG file.
    """
    fig, ax = plt.subplots(figsize=(18,10))

    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Amplitude')
    ax.set_title("Brain Scan")
    
    # last_min = df.loc[0,'timestamp'] + datetime.timedelta(minutes=1)
    
    # df = df[df['timestamp']<=last_min]
    time = df['timestamp'].values
    for column in df.columns:
        if column == 'timestamp':
            continue
        ax.plot(time, df[column].values, label=column)
        
    fig.tight_layout()
    ax.legend(loc='upper right')
    plt.savefig(f'{part}_{file_index}.png')
    plt.show()


def plot_raw_eeg(data, chart_name:str="eeg_plot"):
    for stream in data:
        y = stream["time_series"]

        if isinstance(y, list):
            # list of strings, draw one vertical line for each marker
            for timestamp, marker in zip(stream["time_stamps"], y):
                plt.axvline(x=timestamp)
                print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
        elif isinstance(y, np.ndarray):
            # numeric data, draw as lines
            plt.plot(stream["time_stamps"], y)
        else:
            raise RuntimeError("Unknown stream format")

    plt.savefig(f"{chart_name}.png")


def remove_empty_channels(array:np.array):
    n_channels, _ = array.shape
    has_value = False # if a stream has value
    new_array = np.copy(array)
    for channel in range(n_channels):
        if np.all(array[channel]==0):
            np.delete(new_array, np.where(new_array==array[channel]))
        else:
            has_value = True
    if has_value:
        return new_array
    else:
        return np.zeros(array.shape)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def init_ch_waves(band_names:list):
    ch_waves = {}
    for band in band_names:
        ch_waves[band] = []
    return ch_waves


def get_wave_values(freq:np.array, pow:np.array, band_values:tuple):
    fmin, fmax = band_values
    # min_idx = np.where(freq==fmin)
    print(freq)
    if np.all(freq==0): # temp fix
        return pow
    try:
        min_idx = list(freq).index(fmin)
    except:
        min_idx = find_nearest(freq, fmin)
    try:
        max_idx = list(freq).index(fmax)
    except:
        max_idx = find_nearest(freq, fmax)
    return pow[min_idx:max_idx]


def extract_all_seq_waves(freq:np.array, pow:np.array, bands:dict):
    seq_waves = {}
    for band in bands.keys():
        seq_wave = get_wave_values(freq, pow, bands[band])
        seq_waves[band] = seq_wave
    return seq_waves

def channel_psd(ch_psd:list[tuple[np.array, np.array]], bands:dict):
    ch_waves = init_ch_waves(bands.keys()) # dict of lists
    for i, tup in enumerate(ch_psd):
        freq, pow = tup
        seq_waves = extract_all_seq_waves(freq, pow, bands)
        for wave in seq_waves.keys():
            try: # temp fix
                val = seq_waves[wave].mean()
            except:
                val = seq_waves[wave]
            ch_waves[wave].append(val)
    return ch_waves


def get_xdf_data(file_name:str): 
    dir_path = os.getcwd()
    data_path = os.path.join(dir_path, "data", f"{file_name}.xdf")
    streams, header = pyxdf.load_xdf(data_path)
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
    return stream_list

def show_xdf_data(file_name:str): 
    dir_path = os.getcwd()
    data_path = os.path.join(dir_path, "data", f"{file_name}.xdf")
    streams, header = pyxdf.load_xdf(data_path)

    streams_list = []
    for stream in streams:
        time_stamps = stream['time_stamps']
        data = np.array(stream["time_series"]).T

        new_stamps = np.copy(time_stamps)
        base = time_stamps[0]
        for i, stamp in enumerate(time_stamps):
            new_stamps[i] = stamp - base

        data_tuple = (new_stamps, data)
        streams_list.append(data_tuple)
    return streams_list