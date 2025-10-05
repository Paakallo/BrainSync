from matplotlib import pyplot as plt
import numpy as np
import pyxdf
import mne


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


def plotRawEEG(data, chart_name:str="eeg_plot"):
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


