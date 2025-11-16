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

    def __init__(self, freq1, freq2, duration=0, labrecorder=None):
        self.freq1 = freq1
        self.freq2 = freq2
        self.duration = duration
        self.delay = 0.1 # seconds
        
        self.thread1:threading.Thread = None
        self.thread2:threading.Thread = None

        self.lab_recorder:socket = labrecorder
        self.running = False # running condition for app integration

    def constructNoise(self, y1:np.array, y2:np.array):
        # eye blink, muscle movement, white noise
        return y1, y2

    def filterSignal(self):
        pass

    def constructSignal(self):
        if self.duration == 0:
            print("duration is zero, couldn't construct signals")
            return None, None
        x1 = np.linspace(-np.pi, np.pi, self.freq1*self.duration)
        x2 = np.linspace(-np.pi, np.pi, self.freq2*self.duration)
        y1 = np.sin(x1)
        y2 = np.sin(x2)
        return y1, y2

    def push2inlet(self, outlet:StreamOutlet, signal:list[np.array], freq:int, if_delay:bool=False):
        info = outlet.get_info()
        start_time = local_clock()
        if signal is not None:
            for val in signal:
                print(f"sending {val} from {info.name()}")
                if if_delay:
                    sample_time = (local_clock() - start_time)*(1+self.delay)
                else:
                    sample_time = local_clock() - start_time
                outlet.push_sample([val], sample_time)
                time.sleep(1/freq)
        else:
            self.running = True
            while self.running:
                if if_delay:
                    sample_time = time.time() + self.delay
                    self.delay+=self.delay
                else:
                    sample_time = time.time()
                y = np.sin(2*np.pi*sample_time)
                outlet.push_sample([y], sample_time)
                time.sleep(1/freq)
            print("running was set to False")


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
        y1_outlet = self.createOutlet(name1, type, self.freq1)
        y2_outlet = self.createOutlet(name2, type, self.freq2)

        y1, y2 = self.constructSignal()

        # print("y1_sample length: ", len(y1_samples))
        # print("y2_sample length: ", len(y2_samples))

        # print(y2_samples[0].shape)

        self.thread1 = threading.Thread(target=self.push2inlet, args=(y1_outlet, y1, self.freq1))
        self.thread2 = threading.Thread(target=self.push2inlet, args=(y2_outlet, y2, self.freq2, True))

        if self.lab_recorder is None:
            self.lab_recorder = socket.create_connection(("localhost", 22345))
        self.lab_recorder.sendall(b"update\n")
        self.lab_recorder.sendall(b"select all\n")

        if self.duration != 0:
            answer = input("Press enter to start recording...")
        self.lab_recorder.sendall(b"start\n")
        time.sleep(5.0) # delay for graceful start            
        self.thread1.start()
        self.thread2.start()
        # data recording is stopped externally
        if self.duration != 0:
            self.stopData()

    def stopData(self):
        self.thread1.join()
        self.thread2.join()
        print("Threads finished their job")
        self.lab_recorder.sendall(b"stop\n")
        time.sleep(5.0) # delay for graceful exit
        self.lab_recorder.sendall(b"select none\n")
        self.lab_recorder.close()


if __name__ == "__main__":
    gen = SignalGen(1, 256, 10)
    gen.sendData("stream_1_Hz", "stream_256_Hz")

