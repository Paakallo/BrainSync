import pyxdf
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import argparse

def sync_signals(file_name):
    print(f"Loading {file_name}...")
    streams, header = pyxdf.load_xdf(file_name)

    srates = [float(s['info']['nominal_srate'][0]) for s in streams]
    names = [s['info']['name'][0] for s in streams]
    
    idx_fast = np.argmax(srates)
    idx_slow = np.argmin(srates)
    if idx_fast == idx_slow: idx_slow = 1 - idx_fast

    print(f"Reference Grid (Fast): {names[idx_fast]} ({srates[idx_fast]} Hz)")
    print(f"Interpolating (Slow):  {names[idx_slow]} ({srates[idx_slow]} Hz)")

    t_fast = streams[idx_fast]['time_stamps']
    y_fast = streams[idx_fast]['time_series'][:, 0]

    t_slow = streams[idx_slow]['time_stamps']
    y_slow = streams[idx_slow]['time_series'][:, 0]

    f = interp1d(t_slow, y_slow, kind='linear', fill_value="extrapolate")

    y_slow_resampled = f(t_fast)

    plot_time = t_fast - t_fast[0]

    plt.figure(figsize=(10, 6))
    plt.title("Linear Interpolation (Resampling 1Hz to 256Hz)")
    plt.plot(plot_time, y_fast, label=f"Fast Original ({names[idx_fast]})", 
             color='blue', alpha=0.6, linewidth=1)
    
    plt.plot(plot_time, y_slow_resampled, label=f"Slow Interpolated ({names[idx_slow]})", 
             color='red', alpha=0.8, linestyle='--')

    t_slow_relative = t_slow - t_fast[0]
    plt.scatter(t_slow_relative, y_slow, color='black', marker='x', label="Original 1Hz Points")

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', help="Path to XDF file")
    args = parser.parse_args()
    sync_signals(args.file)