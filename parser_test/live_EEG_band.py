import serial
import matplotlib.pyplot as plt
from collections import deque
import time
import math

def parse_3byte_big_endian(b):
    return (b[0] << 16) | (b[1] << 8) | b[2]

def checksum_is_valid(payload, checksum):
    return (~sum(payload) & 0xFF) == checksum

# Serial port config (adjust 'COM3' as needed)
ser = serial.Serial('/dev/ttyUSB0', 9600)

# Band labels
bands = ["Delta", "Theta", "Low Alpha", "High Alpha", "Low Beta", "High Beta", "Low Gamma", "Mid Gamma"]
band_values = {b: deque([0]*100, maxlen=100) for b in bands}

# Plot setup
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6))
lines = {}

for b in bands:
    (line,) = ax.plot(list(range(100)), list(band_values[b]), label=b)
    lines[b] = line

ax.set_ylim(0, 10)  # log scale
ax.set_xlabel("Time (samples)")
ax.set_ylabel("Log Power")
ax.set_title("Live EEG Power Bands from Mindflex")
ax.legend(loc='upper right')

try:
    while True:
        if ser.read() == b'\xAA' and ser.read() == b'\xAA': # read 2 SYNC bytes
            length = ord(ser.read()) # read PLENGTH byte
            payload = [ord(ser.read()) for _ in range(length)] # read SPAYLOAD bytes
            checksum = ord(ser.read()) # read PCKSUM bye

            if checksum_is_valid(payload, checksum):
                i = 0
                while i < len(payload):
                    code = payload[i]
                    if code == 0x83:
                        raw = payload[i+1:i+25]
                        values = [parse_3byte_big_endian(raw[j:j+3]) for j in range(0, 24, 3)]
                        for b, v in zip(bands, values):
                            # log_v = math.log10(v + 1)  # +1 to avoid log(0)
                            log_v = v
                            print(values)
                            band_values[b].append(log_v)
                        i += 25
                    else:
                        i += 1

                # Update plot
                for b in bands:
                    lines[b].set_ydata(band_values[b])
                plt.pause(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
    ser.close()
