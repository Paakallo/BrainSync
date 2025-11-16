import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from utils import *

# stream_list = show_xdf_data("t_t_1/1/labrecorder/%r")
stream_list = show_xdf_data("%r")


plt.figure()
plt.title("Clock drift")
timestamps, data = stream_list[0]
plt.plot(timestamps, data.flatten(), label="Stream_1_Hz")

timestamps, data = stream_list[1]
plt.plot(timestamps, data.flatten(), label="Stream_256_Hz")

plt.tight_layout()
plt.legend()
plt.show()

