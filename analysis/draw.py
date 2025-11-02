import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from utils import *

stream_list = show_xdf_data("%r")


fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

timestamps, data = stream_list[0]
ax1.plot(timestamps, data.flatten())
ax1.set_title("Stream 0")
ax1.set_xlabel("Sample")
ax1.set_ylabel("Value")

timestamps, data = stream_list[1]
ax2.plot(timestamps, data.flatten())
ax2.set_title("Stream 1")
ax2.set_xlabel("Sample")

plt.tight_layout()

plt.show()

