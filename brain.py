import serial
import time
from pylsl import StreamInfo, StreamOutlet

class Brain:
    def __init__(self, serial_connection: serial.Serial):
        self.current_byte = 'c'
        self.previous_byte = 'c'
        self.is_packet_in_progress = False
        self.packet_buffer = []
        self.packet_length = 0

        self.info_raw = StreamInfo('Mindflex', 'EEG', 1, 1, 'int16', 'RawEEG_UniqueId')
        self.outlet_raw = StreamOutlet(self.info_raw)

        self.continue_running = True
        self.serial_connection = serial_connection
        
        self.data_records = []

    def parse_packet(self, packet_data_list: list):
        """
        Parse the packet data and stream Raw Wave to LSL.
        Other metrics are skipped.
        """
        if self.validate_checksum():
            idx = 1
            while idx < len(self.packet_buffer) - 1:
                packet_type = ord(self.packet_buffer[idx])
                if packet_type == 0x80: # raw values
                    raw_val_high = ord(self.packet_buffer[idx + 2])
                    raw_val_low = ord(self.packet_buffer[idx + 3])
                    
                    raw_val = (raw_val_high << 8) | raw_val_low
                    
                    # Convert to signed 16-bit integer (Two's Complement)
                    if raw_val > 32768:
                        raw_val -= 65536
                    self.outlet_raw.push_sample([raw_val])
                    
                    idx += 4

                elif packet_type == 0x02: # Signal Quality
                    idx += 2
                elif packet_type == 0x04: # Attention
                    idx += 2
                elif packet_type == 0x05: # Meditation
                    idx += 2
                elif packet_type == 0x16: # Blink Strength
                    idx += 2
                elif packet_type == 0x83: # skip brainwaves
                    idx += 26
                else:
                    idx += 1
            
            return packet_data_list
        else:
            print("Invalid checksum!")
            return packet_data_list

    def validate_checksum(self):
        """
        Validate the checksum for the current packet.
        """
        checksum = 0
        for idx in range(1, len(self.packet_buffer) - 1):
            checksum += ord(self.packet_buffer[idx])
        computed_checksum = ~(checksum & 255) & 0xFF
        return computed_checksum == ord(self.packet_buffer[-1])

    def read_serial_data(self):
        """
        Read data from the serial port and process incoming packets.
        """
        if not self.serial_connection.isOpen():
            self.serial_connection.open()
        while self.continue_running:
            try:
                if self.serial_connection.inWaiting() > 0:
                    self.current_byte = self.serial_connection.read(1)

                    if ord(self.previous_byte) == 170 and ord(self.current_byte) == 170 and not self.is_packet_in_progress:
                        self.is_packet_in_progress = True
                    
                    elif len(self.packet_buffer) == 1:
                        self.packet_buffer.append(self.current_byte)
                        self.packet_length = ord(self.packet_buffer[0])
                    
                    elif self.is_packet_in_progress:
                        self.packet_buffer.append(self.current_byte)
                        if len(self.packet_buffer) > 169: 
                            print("Error: Packet too long, clearing buffer")
                            self.packet_buffer.clear()
                            self.is_packet_in_progress = False
                    
                        elif len(self.packet_buffer) == self.packet_length + 2:
                            self.parse_packet(self.data_records)
                            self.packet_buffer.clear()
                            self.is_packet_in_progress = False
                    
                    self.previous_byte = self.current_byte
            except serial.SerialException as e:
                print(f"SerialException occurred: {e}")
                break
            except OSError as e:
                print(f"OSError occurred: {e}")
                break

    def stop_serial_data(self):
        self.continue_running = False
        self.serial_connection.close()