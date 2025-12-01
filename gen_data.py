import socket
import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock
import uuid
import threading

class SignalGen():
    def __init__(self, freq1, freq2, labrecorder=None):
        self.freq1 = freq1
        self.freq2 = freq2
        self.drift_rate = 0.05 
        
        self.thread1 = None
        self.thread2 = None
        self.running = False

        self.lab_recorder = labrecorder
        self.y1_outlet : StreamOutlet = None
        self.y2_outlet : StreamOutlet = None

    def _get_signal_value_at_t(self, t_vector):
        sig = np.sin(2 * np.pi * 0.1 * t_vector) * 10.0
        sig += np.sin(2 * np.pi * 0.23 * t_vector) * 2.0 
        marker_mask = (t_vector % 10.0) < 1.0
        sig[marker_mask] += 30.0
        return sig.astype(np.float32).reshape(-1, 1)

    def _stream_process(self, outlet, freq, is_drifting=False):
        sample_count = 0
        start_time = local_clock() 
        
        target_dt = 0.1
        chunk_size = int(freq * target_dt)
        if chunk_size < 1: chunk_size = 1
        chunk_duration = chunk_size / freq

        while self.running:
            t_logical_vector = (np.arange(chunk_size) + sample_count) / freq
            chunk = self._get_signal_value_at_t(t_logical_vector)
            
            sample_count += chunk_size
            current_logical_time = sample_count / freq
            
            if is_drifting:
                effective_time = start_time + (current_logical_time * (1.0 + self.drift_rate))
            else:
                effective_time = start_time + current_logical_time

            outlet.push_chunk(chunk, effective_time)
            time.sleep(chunk_duration)

    def createOutlet(self, name, type, freq):
        info = StreamInfo(name, type, 1, freq, "float32", str(uuid.uuid1()))
        return StreamOutlet(info)

    def sendData(self, name1, name2, type="EEG"):
        if self.y1_outlet is None and self.y2_outlet is None:
            self.y1_outlet = self.createOutlet(name1, type, self.freq1)
            self.y2_outlet = self.createOutlet(name2, type, self.freq2)
        self.running = True

        time.sleep(1.0)
        self.lab_recorder.sendall(b"update\n")
        time.sleep(0.5)
        self.lab_recorder.sendall(b"select all\n")
        time.sleep(0.2)

        self.thread1 = threading.Thread(target=self._stream_process, args=(self.y1_outlet, self.freq1, False), daemon=True)
        self.thread2 = threading.Thread(target=self._stream_process, args=(self.y2_outlet, self.freq2, True), daemon=True)
        self.thread1.start()
        self.thread2.start()

        
        self.lab_recorder.sendall(b"start\n")
        print("LabRecorder triggered.")

    def stopData(self):
        print("Stopping...")
        self.lab_recorder.sendall(b"stop\n")
        time.sleep(0.5)
        self.running = False 
        self.thread1.join(timeout=1.0)
        self.thread2.join(timeout=1.0)
        print("Done.")