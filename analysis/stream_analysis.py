import pyxdf
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

def load_and_plot_xdf(filename):
    # dir_path = os.getcwd()
    # filename = os.path.join(dir_path, "data", f"{file_name}.xdf")
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    print(f"Loading {filename}...")
    # Load the XDF file
    streams, header = pyxdf.load_xdf(filename)
    print(f"Found {len(streams)} streams.")

    if len(streams) == 0:
        print("No streams found in the file.")
        return

    # Create subplots based on number of streams
    fig, axes = plt.subplots(nrows=len(streams), ncols=1, sharex=True, figsize=(12, 8))
    
    # If there is only one stream, axes is not a list, so we wrap it
    if len(streams) == 1:
        axes = [axes]

    # Iterate through streams and plot them
    for i, stream in enumerate(streams):
        # Extract data
        data = stream['time_series']
        timestamps = stream['time_stamps']
        info = stream['info']
        
        # Get stream metadata
        name = info['name'][0]
        stype = info['type'][0]
        srate = float(info['nominal_srate'][0])
        
        # Handle empty streams
        if len(timestamps) == 0:
            axes[i].text(0.5, 0.5, f"Stream: {name} (Empty)", 
                         horizontalalignment='center', verticalalignment='center',
                         transform=axes[i].transAxes)
            continue

        # Zero the time axis to start at 0 seconds relative to the first sample of this stream
        # (Or align all to the session start if you prefer absolute synchronization)
        times = timestamps - timestamps[0]

        # Plot data
        # If data is multi-channel (e.g. 8 channel EEG), it comes as (n_samples, n_channels)
        if data.ndim > 1 and data.shape[1] > 1:
            # Plot all channels with a slight offset or just overlaid
            # Here we just plot them overlaid with transparency
            axes[i].plot(times, data, alpha=0.7)
            axes[i].set_ylabel(f"{name}\n({data.shape[1]} ch)")
        else:
            # Single channel
            axes[i].plot(times, data)
            axes[i].set_ylabel(f"{name}")

        # Add title details
        axes[i].set_title(f"Stream {i+1}: {srate} Hz", loc='left', fontsize=10)
        axes[i].grid(True, alpha=0.3)

    # Label the bottom x-axis
    axes[-1].set_xlabel("Time (seconds)")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', help="Path to XDF file")
    args = parser.parse_args()
    load_and_plot_xdf(args.file)
    