import pyxdf
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import argparse
import os
import pandas as pd

def sync_signals(file_name, plot_result=True):
    """
    Loads XDF, synchronizes signals via interpolation, and returns the data.
    """
    print(f"[Sync] Loading {file_name}...")
    try:
        streams, header = pyxdf.load_xdf(file_name)
    except Exception as e:
        print(f"[Sync] Error loading XDF: {e}")
        return None, None, None

    # Identify streams based on sampling rate
    if len(streams) < 2:
        print("[Sync] Error: Less than 2 streams found in XDF.")
        return None, None, None

    srates = [float(s['info']['nominal_srate'][0]) for s in streams]
    names = [s['info']['name'][0] for s in streams]
    
    idx_fast = np.argmax(srates)
    idx_slow = np.argmin(srates)
    
    # Handle edge case where rates might be equal or only 1 stream distinct
    if idx_fast == idx_slow: 
        idx_slow = 1 - idx_fast

    print(f"[Sync] Reference (Fast): {names[idx_fast]} ({srates[idx_fast]} Hz)")
    print(f"[Sync] Interpolating (Slow): {names[idx_slow]} ({srates[idx_slow]} Hz)")

    # Extract data
    t_fast = streams[idx_fast]['time_stamps']
    y_fast = streams[idx_fast]['time_series'][:, 0]

    t_slow = streams[idx_slow]['time_stamps']
    y_slow = streams[idx_slow]['time_series'][:, 0]

    # Interpolation
    # We interpolate the Slow signal onto the Fast signal's time grid
    f = interp1d(t_slow, y_slow, kind='linear', fill_value="extrapolate")
    y_slow_resampled = f(t_fast)

    # Plotting (Optional)
    if plot_result:
        plot_time = t_fast - t_fast[0]
        plt.figure(figsize=(10, 6))
        plt.title("Synchronization Result")
        plt.plot(plot_time, y_fast, label=f"Fast ({names[idx_fast]})", color='blue', alpha=0.6)
        plt.plot(plot_time, y_slow_resampled, label=f"Slow Interpolated ({names[idx_slow]})", color='red', alpha=0.8, linestyle='--')
        plt.scatter(t_slow - t_fast[0], y_slow, color='black', marker='x', label="Original Slow Pts")
        plt.legend()
        plt.tight_layout()
        plt.show()

    return t_fast, y_fast, y_slow_resampled

def process_and_save(xdf_path, output_csv_path=None):
    """
    Wrapper to load, sync, and save to CSV.
    """
    if output_csv_path is None:
        output_csv_path = xdf_path.replace(".xdf", "_synced.csv")

    t, y1, y2 = sync_signals(xdf_path, plot_result=False)

    if t is not None:
        print(f"[Sync] Saving synchronized data to: {output_csv_path}")
        
        # Create a DataFrame for easy CSV saving
        df = pd.DataFrame({
            'Timestamp': t,
            'Signal_Fast': y1,
            'Signal_Slow_Interp': y2
        })
        
        df.to_csv(output_csv_path, index=False)
        print("[Sync] Done.")
        return output_csv_path
    else:
        print("[Sync] Failed to generate data.")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?', help="Path to XDF file")
    args = parser.parse_args()
    if args.file:
        sync_signals(args.file)