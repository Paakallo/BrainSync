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

import numpy as np


class SignalGen():

    def __init__(self, freq1, freq2, s_num):
        self.freq1 = freq1
        self.freq2 = freq2
        self.s_num = s_num # s_num liczba próbek, później mnożona przez częstotliwość
        self.start = False

    def constructNoise(self):
        # szum pochodzi od pradu 50 Hz oraz ruchow
        pass

    def filterSignal(self):
        # wpierdol jakies filtry w stylu notcha i innego gowna
        pass

    def constructSignal(self):
        # generuj sygnał tak, że
        # jest całe dzielone na polowe, i te polowki leca pozniej sklejone
        x1 = np.linspace(-np.pi, np.pi, self.freq1*self.s_num)
        x2 = np.linspace(-np.pi, np.pi, self.freq2*self.s_num)
        y1 = np.sin(x1)
        y2 = np.sin(x2)
        

        return y1, y2



    def sendData(self):
        # wysyłaj jeden punkt, co sekunde, wpierdol to gowno w inny watek
        self.start = True
        while self.start:
            y1, y2 = self.constructSignal()
            

