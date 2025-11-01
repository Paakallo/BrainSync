#TODO:
# generate two sinuses: 256 Hz and 1 Hz (maybe selection of freq?)
# add controllable noise

# application:
# LabRecorder frontend:
## Select 2 EEG device
# figure out how to synchronize two signal (marker-based?)
## embed it to labreacorder
## figure it out somehow, how to synchronize


### Links and sources
# good example of sine generator
# https://towardsdatascience.com/use-classes-for-generating-signals-6694d22e9a80/
#
#

import time
from matplotlib import pyplot as plt
import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock
import uuid


class SignalGen():

    def __init__(self, freq1, freq2, duration):
        self.freq1 = freq1
        self.freq2 = freq2
        self.duration = duration 
        self.start = False

    def constructNoise(self, y1:np.array, y2:np.array):
        # eye blink, muscle movement, white noise
        return y1, y2

    def filterSignal(self):
        pass

    def constructSignal(self):
        x1 = np.linspace(-np.pi, np.pi, self.freq1*self.duration)
        x2 = np.linspace(-np.pi, np.pi, self.freq2*self.duration)
        y1 = np.sin(x1)
        y2 = np.sin(x2)
        
        return y1, y2

    def sendData(self, name, type="EEG"):
        # wysyłaj jeden punkt, co sekunde, wpierdol to gowno w inny watek
        y1, y2 = self.constructSignal()

        y1_samples = []
        y2_samples = []
        for i in range(self.duration):
            y1_s = y1[i:i+self.freq1]
            y2_s = y2[i:i+self.freq2]
            y1_samples.append(y1_s)
            y2_samples.append(y2_s)

        print("y1_sample length: ", len(y1_samples))
        print("y2_sample length: ", len(y2_samples))

        print(y2_samples[0].shape)

        y1_info = StreamInfo(name, type, 1, self.freq1, "float32", str(uuid.uuid1()))
        # next make an outlet
        y1_outlet = StreamOutlet(y1_info)

        answer = input("Type anything to start recording...")
        print("now sending data...")
        start_time = local_clock()
        sent_samples = 0
        self.start = True
        while self.start:
            for val in y1:
                print(f"sending {val}...")
                y1_outlet.push_sample([val])
                time.sleep(0.01)
            break

if __name__ == "__main__":
    gen = SignalGen(1, 256, 10)

    gen.sendData("test_stream")

