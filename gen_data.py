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
        self.delay = 0.1 
        
        self.thread1 = None
        self.thread2 = None
        self.running = False
        
        self.lab_recorder = labrecorder

    def _generate_pink_noise(self, samples):
        if samples <= 0: return np.array([])
        state = np.random.randn(samples)
        pink = np.cumsum(state) 
        pink = pink - np.mean(pink)
        return pink / (np.std(pink) + 1e-5)

    def _generate_eeg_chunk(self, n_samples, fs, time_offset):
        if n_samples <= 0: return np.array([])
        
        t = (np.arange(n_samples) + time_offset) / fs
        background = self._generate_pink_noise(n_samples) * 2.0
        # For 1Hz, we just use a slow sine wave
        alpha = np.sin(2 * np.pi * 0.1 * t) * 5.0 
        noise = np.random.randn(n_samples) * 0.1
        
        data = (background + alpha + noise).astype(np.float32)
        # CRITICAL FIX 1: Reshape to (Samples, Channels)
        return data.reshape(-1, 1)

    def _stream_process(self, outlet, freq, if_delay=False):
        sample_counter = 0
        start_time = local_clock()
        
        # Calculate chunk size
        target_dt = 0.1 
        chunk_size = int(freq * target_dt)
        if chunk_size < 1: 
            chunk_size = 1 # Force at least 1 sample (Essential for 1 Hz)
            
        chunk_duration = chunk_size / freq

        while self.running:
            # 1. Generate Data
            chunk = self._generate_eeg_chunk(chunk_size, freq, sample_counter)
            sample_counter += chunk_size

            # 2. Timestamping
            now = local_clock()
            if if_delay:
                push_time = now + (now - start_time) * self.delay
            else:
                push_time = now

            # 3. Push Chunk
            # LSL buffers this. If Recorder starts 0.5s later, 
            # it will still catch this sample from the buffer.
            outlet.push_chunk(chunk, push_time)

            # 4. Sleep
            time.sleep(chunk_duration)

    def createOutlet(self, name, type, freq):
        # Explicitly setting channel_count=1
        info = StreamInfo(name, type, 1, freq, "float32", str(uuid.uuid1()))
        return StreamOutlet(info)

    def sendData(self, name1, name2, type="EEG"):
        if self.running: 
            return

        print(f"Starting Simulation: {name1} ({self.freq1}Hz), {name2} ({self.freq2}Hz)")
        
        # 1. Create Outlets
        self.y1_outlet = self.createOutlet(name1, type, self.freq1)
        self.y2_outlet = self.createOutlet(name2, type, self.freq2)
        
        self.running = True

        # 2. START THREADS IMMEDIATELY (CRITICAL FIX 2)
        # We start pushing data *before* telling LabRecorder to record.
        # This ensures the LSL buffer has data waiting when LabRecorder connects.
        self.thread1 = threading.Thread(target=self._stream_process, 
                                      args=(self.y1_outlet, self.freq1, False), 
                                      daemon=True)
        self.thread2 = threading.Thread(target=self._stream_process, 
                                      args=(self.y2_outlet, self.freq2, True), 
                                      daemon=True)
        self.thread1.start()
        self.thread2.start()

        # 3. Handle LabRecorder
        if self.lab_recorder:
            try:
                # Give LSL a moment to advertise the streams on the network
                print("Waiting for streams to advertise...")
                time.sleep(1.0) 
                
                print("Triggering LabRecorder...")
                self.lab_recorder.sendall(b"update\n")
                time.sleep(0.5) # Wait for update to process
                self.lab_recorder.sendall(b"select all\n")
                time.sleep(0.1)
                self.lab_recorder.sendall(b"start\n")
                print("LabRecorder Started.")
            except Exception as e:
                print(f"LabRecorder Error: {e}")

    def stopData(self):
        if not self.running:
            return

        print("Stopping Simulation...")
        
        # Stop Recorder FIRST so we don't cut off the end of the stream
        if self.lab_recorder:
            try:
                self.lab_recorder.sendall(b"stop\n")
            except:
                pass

        time.sleep(0.5) # Allow recorder to finalize file
        self.running = False 
        
        if self.thread1: self.thread1.join(timeout=1.0)
        if self.thread2: self.thread2.join(timeout=1.0)
        
        print("Simulation Stopped.")
