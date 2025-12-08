import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('1_synced.csv')
df['Relative_Time'] = df['Timestamp'] - df['Timestamp'].iloc[0]

plt.figure(figsize=(12, 6))
plt.plot(df['Relative_Time'], df['Signal_Fast'], label='Signal Fast', alpha=0.7)
plt.plot(df['Relative_Time'], df['Signal_Slow_Interp'], label='Signal Slow (Interpolated)', linestyle='--', alpha=0.7)

plt.title('Synchronized Signals')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()