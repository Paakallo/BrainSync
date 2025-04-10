import serial
import matplotlib.pyplot as plt
from collections import deque
import time

def checksum_is_valid(payload, checksum):
    return (~sum(payload) & 0xFF) == checksum

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Update port

# Setup for plotting
plt.ion()
fig, ax = plt.subplots()
attention_vals = deque([0]*100, maxlen=100)
meditation_vals = deque([0]*100, maxlen=100)
x_vals = list(range(len(attention_vals)))

att_line, = ax.plot(x_vals, attention_vals, label='Attention')
med_line, = ax.plot(x_vals, meditation_vals, label='Meditation')
ax.set_ylim(0, 100)
ax.set_ylabel("Level")
ax.set_xlabel("Time (samples)")
ax.legend()
plt.title("Live Mindflex EEG: Attention & Meditation")

try:
    while True:
        if ser.read() == b'\xAA' and ser.read() == b'\xAA':
            length = ord(ser.read())
            payload = [ord(ser.read()) for _ in range(length)]
            checksum = ord(ser.read())

            if checksum_is_valid(payload, checksum):
                i = 0
                attention = None
                meditation = None

                while i < len(payload):
                    code = payload[i]
                    if code == 0x04:
                        attention = payload[i + 1]
                        i += 2
                    elif code == 0x05:
                        meditation = payload[i + 1]
                        i += 2
                    else:
                        i += 1

                if attention is not None:
                    attention_vals.append(attention)
                else:
                    attention_vals.append(attention_vals[-1])

                if meditation is not None:
                    meditation_vals.append(meditation)
                else:
                    meditation_vals.append(meditation_vals[-1])

                # Update the plot
                att_line.set_ydata(attention_vals)
                med_line.set_ydata(meditation_vals)
                plt.pause(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
    ser.close()
