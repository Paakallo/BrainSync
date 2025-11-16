import time
import numpy as np
import matplotlib.pyplot as plt
import threading

delay = 0.01

def build_signal(data, timestamps, freq, duration, delay, is_delay):
    start = time.time()
    sample_time = start
    offset = 0 # delay from previous iteration
    while sample_time - start < 30: # lab recording duration
        x_range = np.linspace(-np.pi, np.pi, freq*duration)
        signal = np.sin(x_range)
        delay = 0.01
        for y in signal:
            if not is_delay:
                sample_time = time.time() - start
            else:
                sample_time = time.time() - start + delay + offset
                delay+=delay
                print(delay)
                if y == signal[-1]:
                    offset = delay
            timestamps.append(sample_time)
            # print(f"Sending {y}")
            data.append(y)
            time.sleep(1/freq)


data_1 = []
timestamps_1 = []

data_256 = []
timestamps_256 = []


duration = 10

thread_1 = threading.Thread(target=build_signal, args=(data_1, timestamps_1, 1, duration, delay, True))
thread_2 = threading.Thread(target=build_signal, args=(data_256, timestamps_256, 256, duration, delay, False))

thread_1.start()
thread_2.start()


thread_1.join()
thread_2.join()

plt.figure()
plt.title("Clock drift")
plt.plot(timestamps_1, data_1, label="Stream_1_Hz")
plt.plot(timestamps_256, data_256, label="Stream_256_Hz")

plt.tight_layout()
plt.legend()
plt.show()