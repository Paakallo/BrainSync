import time
import numpy as np
import matplotlib.pyplot as plt
import threading



def build_signal(data, timestamps, freq, duration):
    start = time.time()
    sample_time = start
    while sample_time - start < 30: # lab recording duration
        x_range = np.linspace(-np.pi, np.pi, freq*duration)
        signal = np.sin(x_range) 
        for y in signal:
            sample_time = time.time()
            timestamps.append(sample_time)
            print(f"Sending {y}")
            data.append(y)
            time.sleep(1/freq)


data_1 = []
timestamps_1 = []

data_256 = []
timestamps_256 = []


duration = 10

thread_1 = threading.Thread(target=build_signal, args=(data_1, timestamps_1, 1, duration))
thread_2 = threading.Thread(target=build_signal, args=(data_256, timestamps_256, 256, duration))

thread_1.start()
thread_2.start()


# thread_1.join()
thread_2.join()

plt.figure()
plt.title("Clock drift")
plt.plot(timestamps_1, data_1, label="Stream_1_Hz")
plt.plot(timestamps_256, data_256, label="Stream_256_Hz")

plt.tight_layout()
plt.legend()
plt.show()