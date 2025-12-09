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
    try:
        streams, header = pyxdf.load_xdf(file_name)
    except Exception as e:
        print(f"[Sync] Error loading XDF: {e}")
        return None, None, None

    if len(streams) < 2:
        print("[Sync] Error: Less than 2 streams found in XDF.")
        return None, None, None

    srates = [float(s['info']['nominal_srate'][0]) for s in streams]
    
    idx_fast = np.argmax(srates)
    idx_slow = np.argmin(srates)
    
    t_fast = streams[idx_fast]['time_stamps']
    y_fast = streams[idx_fast]['time_series'][:, 0]

    t_slow = streams[idx_slow]['time_stamps']
    y_slow = streams[idx_slow]['time_series'][:, 0]

    f = interp1d(t_slow, y_slow, kind='linear', fill_value="extrapolate")
    y_slow_resampled = f(t_fast)
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
        df = pd.DataFrame({
            'Timestamp': t,
            'Signal_Fast': y1,
            'Signal_Slow_Interp': y2
        })
        df.to_csv(output_csv_path, index=False)
        return output_csv_path
    else:
        return None
