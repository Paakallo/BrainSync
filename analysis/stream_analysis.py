import pyxdf
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

def load_and_plot_xdf(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    streams, header = pyxdf.load_xdf(filename)

    if len(streams) < 2:
        print("Insufficient number of streams")
        return

    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 8))
    
    for i, stream in enumerate(streams):
        data = stream['time_series']
        timestamps = stream['time_stamps']
        info = stream['info']
        
        name = info['name'][0]
        stype = info['type'][0]
        srate = float(info['nominal_srate'][0])
        
        if len(timestamps) == 0:
            axes[i].text(0.5, 0.5, f"Stream: {name} (Empty)", 
                         horizontalalignment='center', verticalalignment='center',
                         transform=axes[i].transAxes)
            continue

        times = timestamps - timestamps[0]

        if data.ndim > 1 and data.shape[1] > 1:
            axes[i].plot(times, data, alpha=0.7)
            # axes[i].set_ylabel(f"{name}\n({data.shape[1]} ch)")
        else:
            axes[i].plot(times, data)
            # axes[i].set_ylabel(f"{name}")

        axes[i].set_title(f"Stream {i+1}: {srate} Hz", loc='left', fontsize=10)
        axes[i].grid(True, alpha=0.3)

    axes[-1].set_xlabel("Time (seconds)")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot XDF streams based on username, session part and filename.")
    parser.add_argument("username", type=str)
    parser.add_argument("session", type=int, help="session part")
    parser.add_argument("filename", type=str, help="filename without extension")
    
    args = parser.parse_args()
    file_path = f"data/{args.username}/{args.session}/labrecorder/{args.filename}.xdf"
    load_and_plot_xdf(file_path)