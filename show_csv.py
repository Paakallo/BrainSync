import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

parser = argparse.ArgumentParser(description='Plot synchronized signals from a CSV file.')
parser.add_argument('username', type=str)
parser.add_argument('session', type=str, help='session part')
parser.add_argument('filename', type=str, help='filename without _sync.csv extension')

args = parser.parse_args()

csv_path = f"data/{args.username}/{args.session}/labrecorder/{args.filename}_synced.csv"

if not os.path.exists(csv_path):
    print(f"Error: File not found at {csv_path}")
    exit(1)

df = pd.read_csv(csv_path)
df['Relative_Time'] = df['Timestamp'] - df['Timestamp'].iloc[0]

plt.figure(figsize=(12, 6))
plt.plot(df['Relative_Time'], df['Signal_Fast'], label='Signal Fast', alpha=0.7)
plt.plot(df['Relative_Time'], df['Signal_Slow_Interp'], label='Signal Slow (Interpolated)', linestyle='--', alpha=0.7)

plt.title(f'Synchronized Signals: {args.filename}')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()