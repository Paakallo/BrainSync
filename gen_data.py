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

import socket
import time
from matplotlib import pyplot as plt
import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock
import uuid
import threading

class SignalGen():

    def __init__(self, freq1, freq2, duration):
        self.freq1 = freq1
        self.freq2 = freq2
        self.duration = duration

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

    def push2inlet(self, outlet:StreamOutlet, signal:list[np.array], freq:int):
        info = outlet.get_info()
        for val in signal:
            print(f"sending {val} from {info.name()}")
            outlet.push_sample([val])
            time.sleep(1/freq)

    def divideChunks(self, signal:np.array, freq:int):
        samples: list[np.array] = []
        for i in range(self.duration):
            sample = signal[i:i+freq]
            samples.append(sample)
        return samples

    def createOutlet(self, name:str, type:str, freq:int):
        info = StreamInfo(name, type, 1, freq, "float32", str(uuid.uuid1()))
        outlet = StreamOutlet(info)
        return outlet

    def sendData(self, name1, name2, type="EEG"):
        y1, y2 = self.constructSignal()

        # print("y1_sample length: ", len(y1_samples))
        # print("y2_sample length: ", len(y2_samples))

        # print(y2_samples[0].shape)

        y1_outlet = self.createOutlet(name1, type, self.freq1)
        # y2_outlet = self.createOutlet(name2, type, self.freq2)
        
        thread1 = threading.Thread(target=self.push2inlet, args=(y1_outlet, y1, self.freq1))
        # thread2 = threading.Thread(target=self.push2inlet, args=(y2_outlet, y2, self.freq2))

        lab_recorder = socket.create_connection(("localhost", 22345))
        lab_recorder.sendall(b"update\n")
        lab_recorder.sendall(b"select all\n")

        answer = input("Type anything to start recording...")
        # lab_recorder.sendall(b"start\n")
        
        thread1.start()
        # thread2.start()

        thread1.join()

        time.sleep(5.0)
        # lab_recorder.sendall(b"stop\n")
        time.sleep(2.0)
        # lab_recorder.sendall(b"select none\n")
        time.sleep(5.0)
        lab_recorder.close()

if __name__ == "__main__":
    gen = SignalGen(1, 256, 10)
    gen.sendData("stream_1_Hz", "stream_256_Hz")

