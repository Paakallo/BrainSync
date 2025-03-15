import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

import json
import sys
import time
# from datetime import datetime


class Brain:
    def __init__(self, serial_connection:serial.Serial):
        # Variables related to packet handling
        self.current_byte = 'c'
        self.previous_byte = 'c'
        self.is_packet_in_progress = False
        self.packet_buffer = []
        self.packet_length = 0

        # EEG data variables
        self.eeg_values = []
        self.eeg_raw_value = []

        # Control flag
        self.continue_running = True
        self.serial_connection = serial_connection

        self.data_records = []

    def parse_packet(self, packet_data_list:list):
        """
        Parse the packet data and extract relevant EEG metrics.
        """
        if self.validate_checksum():
            idx = 1
            while idx < len(self.packet_buffer) - 1:
                packet_type = ord(self.packet_buffer[idx])
                
                if packet_type == 0x02:
                    signal_strength = ord(self.packet_buffer[idx + 1])
                    idx += 2
                elif packet_type == 0x04:
                    attention = ord(self.packet_buffer[idx + 1])
                    idx += 2
                elif packet_type == 0x05:
                    meditation = ord(self.packet_buffer[idx + 1])
                    idx += 2
                elif packet_type == 0x16:
                    blink_strength = ord(self.packet_buffer[idx + 1])
                    idx += 2
                elif packet_type == 0x83:
                    for count in range(idx + 1, idx + 25, 3):
                        self.eeg_values.append(
                            ord(self.packet_buffer[count]) << 16 | 
                            ord(self.packet_buffer[count + 1]) << 8 | 
                            ord(self.packet_buffer[count + 2])
                        )
                    idx += 26
                elif packet_type == 0x80:
                    eeg_raw_value = ord(self.packet_buffer[idx + 1]) << 8 | ord(self.packet_buffer[idx + 2])
                    idx += 4
            
            print(f"{signal_strength},         {attention},         {meditation},{'         ,'.join(map(str, self.eeg_values))}")
            
            packet_data_list.append([
                datetime.datetime.now(),
                signal_strength,
                attention,
                meditation,
                *self.eeg_values
            ])
            
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
        # global packet_buffer, previous_byte, current_byte, is_packet_in_progress, packet_length, continue_running

        # Initialize serial port
        # serial_connection = serial.Serial(
        #     port=com_port,
        #     baudrate=9600,
        #     parity=serial.PARITY_NONE,
        #     stopbits=serial.STOPBITS_ONE,
        #     bytesize=serial.SEVENBITS
        # )

        self.serial_connection.isOpen()
        print("self.serial_connection.isOpen()")

        while self.continue_running:
            if self.serial_connection.inWaiting() > 0:
                self.current_byte = self.serial_connection.read(1)

                if ord(self.previous_byte) == 170 and ord(self.current_byte) == 170 and not self.is_packet_in_progress:
                    self.is_packet_in_progress = True
                elif len(self.packet_buffer) == 1:
                    self.packet_buffer.append(self.current_byte)
                    self.packet_length = ord(self.packet_buffer[0])
                elif self.is_packet_in_progress:
                    self.packet_buffer.append(self.current_byte)

                    # Validate packet length
                    if len(self.packet_buffer) > 169:
                        print("Error: Data error too long!")
                        self.packet_buffer.clear()
                        self.is_packet_in_progress = False
                        self.eeg_values.clear()

                    elif len(self.packet_buffer) == self.packet_length + 2:
                        self.data_records = self.parse_packet(self.data_records)
                        self.packet_buffer.clear()
                        self.is_packet_in_progress = False
                        self.eeg_values.clear()

                self.previous_byte = self.current_byte
            else:
                print("Waiting for connection")

    def stop_serial_data(self):
        self.continue_running = False
        self.serial_connection.close()
        #TODO: reset object
        return self.data_records

    