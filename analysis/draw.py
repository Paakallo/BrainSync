import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from utils import plot_eeg_data



df = pd.read_csv("data/Sergiusz_Pyskowacki_21/1/mindflex/1_1.csv")
plot_eeg_data(df, "1", "1")


