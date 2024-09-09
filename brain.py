import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

# Variables related to packet handling
current_byte = 'c'
previous_byte = 'c'
is_packet_in_progress = False
packet_buffer = []
packet_length = 0

# EEG data variables
eeg_values = []
eeg_raw_value = []

# Control flag
continue_running = True

def parse_packet(packet_data_list:list):
    """
    Parse the packet data and extract relevant EEG metrics.
    """
    if validate_checksum():
        idx = 1
        while idx < len(packet_buffer) - 1:
            packet_type = ord(packet_buffer[idx])
            
            if packet_type == 0x02:
                signal_strength = ord(packet_buffer[idx + 1])
                idx += 2
            elif packet_type == 0x04:
                attention = ord(packet_buffer[idx + 1])
                idx += 2
            elif packet_type == 0x05:
                meditation = ord(packet_buffer[idx + 1])
                idx += 2
            elif packet_type == 0x16:
                blink_strength = ord(packet_buffer[idx + 1])
                idx += 2
            elif packet_type == 0x83:
                for count in range(idx + 1, idx + 25, 3):
                    eeg_values.append(
                        ord(packet_buffer[count]) << 16 | 
                        ord(packet_buffer[count + 1]) << 8 | 
                        ord(packet_buffer[count + 2])
                    )
                idx += 26
            elif packet_type == 0x80:
                eeg_raw_value = ord(packet_buffer[idx + 1]) << 8 | ord(packet_buffer[idx + 2])
                idx += 4
        
        print(f"{signal_strength},         {attention},         {meditation},{'         ,'.join(map(str, eeg_values))}")
        
        packet_data_list.append([
            datetime.datetime.now(),
            signal_strength,
            attention,
            meditation,
            *eeg_values
        ])
        
        return packet_data_list
    else:
        print("Invalid checksum!")
        return packet_data_list

def validate_checksum():
    """
    Validate the checksum for the current packet.
    """
    checksum = 0
    for idx in range(1, len(packet_buffer) - 1):
        checksum += ord(packet_buffer[idx])
    
    computed_checksum = ~(checksum & 255) & 0xFF
    return computed_checksum == ord(packet_buffer[-1])

def read_serial_data(com_port,name,surname,age):
    """
    Read data from the serial port and process incoming packets.
    """
    global packet_buffer, previous_byte, current_byte, is_packet_in_progress, packet_length, continue_running

    # Initialize serial port
    serial_connection = serial.Serial(
        port=com_port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS
    )

    data_records = []
    serial_connection.isOpen()

    try:
        while continue_running:
            if serial_connection.inWaiting() > 0:
                current_byte = serial_connection.read(1)

                if ord(previous_byte) == 170 and ord(current_byte) == 170 and not is_packet_in_progress:
                    is_packet_in_progress = True
                elif len(packet_buffer) == 1:
                    packet_buffer.append(current_byte)
                    packet_length = ord(packet_buffer[0])
                elif is_packet_in_progress:
                    packet_buffer.append(current_byte)

                    # Validate packet length
                    if len(packet_buffer) > 169:
                        print("Error: Data error too long!")
                        packet_buffer.clear()
                        is_packet_in_progress = False
                        eeg_values.clear()

                    elif len(packet_buffer) == packet_length + 2:
                        data_records = parse_packet(data_records)
                        packet_buffer.clear()
                        is_packet_in_progress = False
                        eeg_values.clear()

                previous_byte = current_byte

    except KeyboardInterrupt:
        print("Exiting...")
        save_data_to_csv(data_records, serial_connection,name,surname,age)

def save_data_to_csv(data, serial_connection,name,surname,age):
    """
    Save the collected EEG data to a CSV file and plot the data.
    """
    if not os.path.exists('data'):
        os.mkdir('data')
    df = pd.DataFrame(data, columns=[
        'timestamp', 'signal_strength', 'attention', 'meditation',
        'delta', 'theta', 'low_alpha', 'high_alpha', 'low_beta', 'high_beta', 
        'low_gamma', 'high_gamma'
    ])

    # df['timestamp'] = df['timestamp'] - df.loc[0, 'timestamp']

    if not os.path.exists(f'{name}{surname}{age}'):    
    	os.mkdir(f'{name}{surname}{age}')

    file_index = check_file(name,surname,age)
    df.to_csv(f'{name}{surname}{age}/{datetime.date.today()}_{file_index}.csv', index=False)

    if serial_connection.isOpen():
        serial_connection.close()

    plot_eeg_data(df, file_index,name,surname,age)

def plot_eeg_data(df, file_index,name,surname,age):
    """
    Plot the EEG data and save the plot as a PNG file.
    """
    fig, ax = plt.subplots(figsize=(18,10))

    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Amplitude')
    ax.set_title("Brain Scan")
    
    last_min = df.loc[0,'timestamp'] + datetime.timedelta(minutes=1)
    
    df = df[df['timestamp']<=last_min]
    time = df['timestamp'].values
    for column in df.columns:
        if column == 'timestamp':
            continue
        ax.plot(time, df[column].values, label=column)
        
    fig.tight_layout()
    ax.legend(loc='upper right')
    plt.savefig(f'{name}{surname}{age}/{datetime.date.today()}_{file_index}.png')
    plt.show()

def check_file(name,surname,age):
    file_index = 1
    while os.path.exists(f'{name}{surname}{age}/{datetime.date.today()}_{file_index}.csv'):
        file_index += 1
    return file_index
def main(name,surname,age):

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <COM PORT>")
        sys.exit(1)

    check_no = True
    while check_no:
        num = int(input("Type procedure part"))
        if os.path.exists(f'{name}{surname}{age}/{datetime.date.today()}_{num}.csv'):
            answer = input('This procedure has been completed, do you want to rewrite a file?\n Type Y|N (Yes|No)')
            answer = answer.upper()

            if answer == 'Y':
                os.remove(f'{name}{surname}{age}/{datetime.date.today()}_{num}.csv')
                check_no = False
            elif answer == 'N':
                continue
        else:
            check_no = False
    input("Press Enter to start reading data...")
    print('timestamp   ', 'signal_strength   ', 'attention   ', 'meditation   ',
        'delta   ', 'theta   ', 'low_alpha   ', 'high_alpha   ', 'low_beta   ', 'high_beta   ',
        'low_gamma   ', 'high_gamma   ')
    read_serial_data(sys.argv[1],name,surname,age)


if __name__ == '__main__':
    name = input('Type Name:')
    surname = input('Type Surname:')
    age = input('Type Age:')

    if not os.path.exists(f'{name}{surname}{age}'):    
    	os.mkdir(f'{name}{surname}{age}')
    else:
        print('This folder already exists')
    
    while True:
    	main(name,surname,age)