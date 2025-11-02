import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from utils import *

stream_list = get_xdf_data("%r")

print("Signal count: ", len(stream_list))

data = stream_list[0]
print("First signal: ", data.shape)
data = stream_list[1]
print("Second signal: ", data.shape)

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

ax1.plot(stream_list[0].flatten())
ax1.set_title("Stream 0")
ax1.set_xlabel("Sample")
ax1.set_ylabel("Value")

ax2.plot(stream_list[1].flatten())
ax2.set_title("Stream 1")
ax2.set_xlabel("Sample")

plt.tight_layout()

plt.show()

