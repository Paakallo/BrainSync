import serial

def parse_3byte_big_endian(b):
    return (b[0] << 16) | (b[1] << 8) | b[2]

def format_eeg_bands(eeg_values):
    labels = [
        "Delta", "Theta", "Low Alpha", "High Alpha",
        "Low Beta", "High Beta", "Low Gamma", "Mid Gamma"
    ]
    return {label: val for label, val in zip(labels, eeg_values)}

def main():
    # Update COM port and baud rate as needed
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Use '/dev/ttyUSB0' or '/dev/ttyS0' on Linux

    print("Listening to Mindflex... Press Ctrl+C to stop.\n")

    try:
        while True:
            # Look for sync bytes 0xAA 0xAA
            if ser.read() == b'\xaa' and ser.read() == b'\xaa':
                payload_len = ord(ser.read())
                payload = [ord(ser.read()) for _ in range(payload_len)]
                checksum = ord(ser.read())

                # Validate checksum
                if (~sum(payload) & 0xFF) == checksum:
                    i = 0
                    attention = None
                    meditation = None
                    poor_signal = None
                    eeg_values = None

                    while i < len(payload):
                        code = payload[i]
                        if code == 0x02:  # Poor signal
                            poor_signal = payload[i+1]
                            i += 2
                        elif code == 0x04:  # Attention
                            attention = payload[i+1]
                            i += 2
                        elif code == 0x05:  # Meditation
                            meditation = payload[i+1]
                            i += 2
                        elif code == 0x83:  # EEG Power
                            eeg_raw = [parse_3byte_big_endian(payload[i + j:i + j + 3]) for j in range(1, 25, 3)]
                            eeg_values = format_eeg_bands(eeg_raw)
                            i += 25
                        else:
                            i += 1  # Skip unknown

                    # Print the parsed data
                    print("------ Mindflex Data ------")
                    if poor_signal is not None:
                        print(f"Signal Quality: {'Poor' if poor_signal > 0 else 'Good'} ({poor_signal})")
                    if attention is not None:
                        print(f"Attention: {attention}")
                    if meditation is not None:
                        print(f"Meditation: {meditation}")
                    if eeg_values is not None:
                        print("EEG Bands:")
                        for band, value in eeg_values.items():
                            print(f"  {band}: {value}")
                    print("---------------------------\n")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
