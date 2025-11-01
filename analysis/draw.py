import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from utils import *

stream_list = get_xdf_data("test3")


data = stream_list[0]
print(data.shape)
plt.figure()


plt.plot(data.flatten())

plt.show()

