import numpy as np
import serial
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

import json
import sys
import time

def save_data(data, part:int, filename):
    """
    Save the collected EEG data to a CSV file and plot the data.
    """
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'signal_strength', 'attention', 'meditation',
        'delta', 'theta', 'low_alpha', 'high_alpha', 'low_beta', 'high_beta', 
        'low_gamma', 'high_gamma'
    ])

    file_index = check_file(part, filename)
    df.to_csv(f'{filename}/{part}/mindflex/{part}_{file_index}.csv', index=False)

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
            path = os.path.join("data", f"{name}_{surname}_{age}")
            os.remove(path) #potentially dangerous
            os.makedirs(path) 
            break
    with open("patients.json", "w") as file:
            json.dump(pat_list, file)

def remove_patient(name,surname,age):
    with open("patients.json", "r") as file:
        pat_list = json.load(file)
    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            pat_list.remove(pat)
            path = os.path.join("data", f"{name}_{surname}_{age}")
            os.remove(path) 
            break
    with open("patients.json", "w") as file:
            json.dump(pat_list, file)

def remove_part(name,surname,age, part):
    with open("patients.json", "r") as file:
        pat_list = json.load(file)
    for pat in pat_list:
        if pat['Name'] == name and pat['Surname'] == surname and pat['Age'] == age:
            path = os.path.join("data", f"{name}_{surname}_{age}", f"{part}")
            os.remove(path) 
            break
    with open("patients.json", "w") as file:
            json.dump(pat_list, file)

def connect2headset(port="COM5"):
    if sys.platform == 'linux':
        serial_connection = serial.Serial(
            # assume port is assigned to headset
            port="/dev/ttyUSB0",
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS 
        )     
    else:
        # assume COM port is assigned to headset
        serial_connection = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS
        )
    return serial_connection

def add_run_path(name, surname, age, part_no, run_no, file_path):
    """
    Appends the run number and file path to the specific part list in patients.json.
    """
    json_path = "patients.json"
    if not os.path.exists(json_path):
        return False
    with open(json_path, "r") as file:
        pat_list = json.load(file)
    found = False
    for pat in pat_list:
        if pat['Name'] == str(name) and pat['Surname'] == str(surname) and pat['Age'] == str(age):
            part_key = f"part_{part_no}"
            if part_key not in pat:
                pat[part_key] = []
            new_record = {
                "run": run_no,
                "path": file_path,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            pat[part_key].append(new_record)
            found = True
            break
    if found:
        with open(json_path, "w") as file:
            json.dump(pat_list, file, indent=4)
        return True
    else:
        print(f"[JSON] Error: Patient {name} {surname} not found.")
        return False