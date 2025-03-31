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


### STOP functions
def save_data(data, part:int, filename):
    """
    Save the collected EEG data to a CSV file and plot the data.
    """
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'signal_strength', 'attention', 'meditation',
        'delta', 'theta', 'low_alpha', 'high_alpha', 'low_beta', 'high_beta', 
        'low_gamma', 'high_gamma'
    ])

    # df['timestamp'] = df['timestamp'] - df.loc[0, 'timestamp']

    # if not os.path.exists(f'{name}{surname}{age}'):    
    # 	os.mkdir(f'{name}{surname}{age}')

    file_index = check_file(part, filename)
    df.to_csv(f'{filename}/{part}/mindflex/{part}_{file_index}.csv', index=False)
    # plot_eeg_data(df, part, file_index)

def plot_eeg_data(df, part, file_index):
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
    plt.savefig(f'{part}_{file_index}.png')
    plt.show()

def check_file(part, filename):
    file_index = 1
    while os.path.exists(f'{filename}/{part}/mindflex/{part}_{file_index}.csv'):
        file_index += 1
    return file_index


def check_patient(name, surname, age, pat_list): 
    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            return True
    return False

def add_patient(name, surname, age):
    if not os.path.exists("patients.json"):
        with open("patients.json", "w") as file:
            json.dump([],file)

    with open("patients.json", "r") as file:
        pat_list = json.load(file)
    
    if check_patient(name,surname,age,pat_list):
        return False
    else:
        # create patient data card in json
        path = os.path.join("data", f"{name}_{surname}_{age}")
        os.makedirs(path)
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        person = {
            "Name": name,
            "Surname": surname,
            "Age": age,
            "created_ago": f"{date}",
            "created_at" : path,
            "part_no": 0,
            "part_1": [],
            "part_2": [],
            "part_3": []
        }
        pat_list.append(person)

        with open("patients.json", "w") as file:
            json.dump(pat_list, file)
        return True

def load_patient(name,surname,age):
    with open("patients.json", "r") as file:
        pat_list = json.load(file)
    if check_patient(name,surname,age,pat_list):
        return []
    
    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            return pat
    return []

def update_patient(name,surname,age,part_no):
    with open("patients.json", "r") as file:
        pat_list = json.load(file)

    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            pat['part_no'] = part_no
            break
    with open("patients.json", "w") as file:
            json.dump(pat_list, file)

def reset_patient(name,surname,age):
    with open("patients.json", "r") as file:
        pat_list = json.load(file)

    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            pat['part_no'] = 0
            pat['part_1'] = []
            pat['part_2'] = []
            pat['part_3'] = []
            break
    with open("patients.json", "w") as file:
            json.dump(pat_list, file)

def connect2headset():
    if sys.platform == 'linux':
        serial_connection = serial.Serial(
            # assume port is assigned to headset
            port="/dev/rfcomm0",
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS 
        )     
    else:
        # assume COM port is assigned to headset
        serial_connection = serial.Serial(
            port="COM5",
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS
        )
    return serial_connection