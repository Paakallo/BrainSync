import tkinter as tk
from tkinter import messagebox
from tkinter import dialog
from brain import Brain
from utils import *
from gen_data import SignalGen
import threading
import socket
import argparse
import os

# Tutaj labrecorder frontend

class MainWindow(tk.Tk):
    def __init__(self, use_lab:bool, use_sim:bool):
        super().__init__()
        self.title("BrainSync")
        self.geometry("1000x1000")

        self.start_button = tk.Button(self, text="Start", command=self.start_record)
        self.start_button.pack()

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_record)
        self.stop_button.pack()

        # self.continue_button = tk.Button(self, text="Abort", command=self.abort_record)
        # self.continue_button.pack()

        self.select_button = tk.Button(self, text="Select patient", command=self.select_patient)
        self.select_button.pack()

        # self.reset_button = tk.Button(self, text="Reset patient", command=self.res_pat)
        # self.reset_button.pack()

        self.rem_part_button = tk.Button(self, text="Remove part", command=self.rem_part)
        self.rem_part_button.pack()

        # self.remove_button = tk.Button(self, text="Remove patient", command=self.rem_pat)
        # self.remove_button.pack()

        self.unset_button = tk.Button(self, text="Unset patient", command=self.unset_pat)
        self.unset_button.pack()

        # Single-selection Listbox for choosing a part
        self.parts_listbox = tk.Listbox(self, selectmode=tk.SINGLE, height=7, exportselection=False)
        for i in range(1,8):
            self.parts_listbox.insert(tk.END, i)
        self.parts_listbox.pack()
        # Button to assign selected part to self.parts
        self.confirm_parts_button = tk.Button(self, text="Set Selected Part", command=self.set_selected_part)
        self.confirm_parts_button.pack()

        # Single-selection Listbox for choosing a part
        self.port_listbox = tk.Listbox(self, selectmode=tk.SINGLE, height=10, exportselection=False)
        for i in range(1,11):
            self.port_listbox.insert(tk.END, i)
        self.port_listbox.pack()
        # Button to assign selected part to self.parts
        self.confirm_port_button = tk.Button(self, text="Set COM Port", command=self.set_port)
        self.confirm_port_button.pack()

        # control booleans
        self.use_lab = use_lab
        self.use_sim = use_sim
        self.lab_recorder = None

        # patient data
        self.name = None
        self.surname = None
        self.age = None

        self.parts = 0
        self.run_no = 0
        self.sel_pat = False
        self.exper:Brain = None

        self.data = []
        self.running = False

        self.start_clicked = False # start button
        self.COM_port = None

        # displayed patient info
        self.info_label = tk.Label(self, text=f"{self.name}_{self.surname}_{self.age}")
        self.info_label.pack()
        self.label = tk.Label(self, text=f"Current Part:{self.parts} \nCurrent run:{self.run_no}")
        self.label.pack()
        self.run_status = tk.Label(self, text=f"Is Running:{self.running}")
        self.run_status.pack()

        # display COM port
        self.port_info = tk.Label(self, text=f"COM{self.COM_port}")
        self.port_info.pack()

        if not os.path.exists('data'):
            os.mkdir('data')

        if self.use_lab:
            self.lab_recorder = socket.create_connection(("localhost", 22345))
            self.lab_recorder.sendall(b"select all\n")

        if self.use_sim:
            self.exer = SignalGen(1, 256, 0, self.lab_recorder)

    def send_msg(self, msg:str):
        if self.use_lab:
            self.lab_recorder.sendall(msg)
    
    def send_start(self):
        if self.use_sim:
            self.exer.sendData("1_Hz", "256_Hz")
        else:
            try:
                self.exper = Brain(connect2headset(f"COM{self.COM_port}"))
                # Run `read_serial_data()` in a separate thread
                self.thread = threading.Thread(target=self.exper.read_serial_data, daemon=True)
                self.thread.start()
                self.send_msg(b"start\n")
            except:
                self._wrong_port_()

    def send_stop(self):
        if self.use_sim:
            self.exer.running = False
            self.exer.stopData()
        else:
            self.exper.continue_running = False  # Stop the loop in `read_serial_data()`
            self.data = self.exper.stop_serial_data()
            self.thread.join(timeout=2)  # Wait for the thread to stop
            self.running = False
            self.send_msg(b"stop\n")
 
    def set_port(self):
        selected = self.port_listbox.curselection()
        if selected:
            self.COM_port = selected[0] + 1 # temporary fix 
            # self.set_lab_dir()
            self.update_COM_label()
            # messagebox.showinfo("Part Set", f"Selected Part: {self.parts}")
        else:
            messagebox.showwarning("No Selection", "Please select a COM port.")

    def set_selected_part(self):
        selected = self.parts_listbox.curselection()
        if selected:
            self.parts = selected[0] + 1 # temporary fix 
            self.set_lab_dir()
            self.update_parts_label()
            messagebox.showinfo("Part Set", f"Selected Part: {self.parts}")
        else:
            messagebox.showwarning("No Selection", "Please select a part.")

    def set_lab_dir(self, run = 1):
        participant = f"{self.name}_{self.surname}_{self.age}"
        # session = self.parts + 1 # current part maybe 0, but when data is saved, current part is 1
        session = self.parts
        param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:Default}} {{modality:eeg}}\n"
        send_msg = b"filename {template:%p/%s/LabRecorder/%r.xdf} " + param_str.encode()
        self.send_msg(send_msg)

    def update_parts_label(self):
        self.label.config(text=f"Current Part: {self.parts} \nCurrent Run:{self.run_no}")   
        self.info_label.config(text=f"{self.name}_{self.surname}_{self.age}")        
        self.run_status.config(text=f"Running status:{self.running}")

    def update_COM_label(self):
        self.port_info.config(text=f"COM{self.COM_port}")

    def _patient_selection_(self, text=''):
        self.dialog = tk.Toplevel()
        self.dialog.title("Patient select")
        label = tk.Label(self.dialog, text=f"Patient {text} selected")
        label.pack()

        self.continue_button = tk.Button(
            self.dialog, text="Continue", command=lambda: self.dialog.destroy())
        self.continue_button.pack()

    def _type_data_(self):
        dialog = tk.Toplevel()
        dialog.title("Enter Patient Information")
        dialog.geometry("300x200")
        
        # Labels and Entry Fields
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        entry_name = tk.Entry(dialog)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Surname:").grid(row=1, column=0, padx=10, pady=5)
        entry_surname = tk.Entry(dialog)
        entry_surname.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Age:").grid(row=2, column=0, padx=10, pady=5)
        entry_age = tk.Entry(dialog)
        entry_age.grid(row=2, column=1, padx=10, pady=5)


        def validate_and_close():
            self.name = entry_name.get().strip()
            self.surname = entry_surname.get().strip()
            self.age = entry_age.get().strip()
            if self.name and self.surname and self.age:
                try:
                    int(self.age)  # Ensure age is a number
                    
                    if not add_patient(self.name, self.surname, self.age):
                        # messagebox.showwarning("Existing record", "Patient already exists")
                        self._sel_existing_()
                        dialog.destroy()
                    else:
                        self.sel_pat = True
                        self.parts = 1
                        self.set_lab_dir()
                        self.update_parts_label()
                        dialog.destroy()
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Age must be a number.")
            else:
                messagebox.showwarning("Missing Fields", "Please fill in all fields.")


        # OK Button
        ok_button = tk.Button(dialog, text="OK", command=validate_and_close)
        ok_button.grid(row=3, column=0, columnspan=2, pady=10)

        dialog.transient()  # Make the dialog modal
        dialog.grab_set()  # Prevent interaction with the main window
        self.wait_window(dialog)  # Wait for the dialog to close
    
    def _sel_existing_(self):
        sel_dialog = tk.Toplevel()
        sel_dialog.title("Patient already exists")
        sel_dialog.geometry("300x200")

        def exit():
            self.name = None
            self.surname = None
            self.age = None
            sel_dialog.destroy()

        def confirm():
            self.parts = 1
            self.set_lab_dir()
            self.update_parts_label()
            self.sel_pat = True
            sel_dialog.destroy()

        exit_button = tk.Button(sel_dialog, text="Exit", command=exit)
        exit_button.grid(row=2, column=3, columnspan=2, pady=10)

        confirm_button = tk.Button(sel_dialog, text="Confirm", command=confirm)
        confirm_button.grid(row=2, column=1, columnspan=2, pady=10)

        sel_dialog.transient()  # Make the dialog modal
        sel_dialog.grab_set()  # Prevent interaction with the main window
        self.wait_window(sel_dialog)  # Wait for the dialog to close

    def _type_run_(self):
        sel_dialog = tk.Toplevel()
        sel_dialog.title("Run section")
        sel_dialog.geometry("300x200")

        tk.Label(sel_dialog, text=f"Current part:{self.parts}").grid(row=1, column=1, padx=10, pady=5)
        tk.Label(sel_dialog, text="Run number:").grid(row=2, column=0, padx=10, pady=5)
        entry_run = tk.Entry(sel_dialog)
        entry_run.grid(row=2, column=1, padx=10, pady=5)

        def validate_and_close():
            self.run_no = entry_run.get().strip()
            if self.run_no:
                try:
                    self.run_no = int(self.run_no)  # Ensure age is a number
                    self.set_lab_dir(self.run_no)
                    self.update_parts_label()
                    sel_dialog.destroy()
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Run number must be a number.")
            else:
                messagebox.showwarning("Missing Fields", "Please fill in all fields.")

        confirm_button = tk.Button(sel_dialog, text="Confirm", command=validate_and_close)
        confirm_button.grid(row=2, column=1, columnspan=2, pady=10)

        sel_dialog.transient()  # Make the dialog modal
        sel_dialog.grab_set()  # Prevent interaction with the main window
        self.wait_window(sel_dialog)  # Wait for the dialog to close

    def _wrong_port_(self):
        sel_dialog = tk.Toplevel()
        sel_dialog.title("Run section")
        sel_dialog.geometry("300x200")
        tk.Label(sel_dialog, text=f"Wrong port: COM{self.COM_port}").grid(row=2, column=1, columnspan=2, pady=10)
        sel_dialog.transient()  # Make the dialog modal
        sel_dialog.grab_set()  # Prevent interaction with the main window
        self.wait_window(sel_dialog)

    def res_pat(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        reset_patient(self.name,self.surname,self.age)
        self.parts = 0
        self.update_parts_label()
    
    def rem_part(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        remove_part(self.name,self.surname,self.age, self.parts)
        if self.parts > 0:
            self.parts -= 1
        else:
            self.parts += 1
        self.update_parts_label()

    def rem_pat(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        remove_patient(self.name,self.surname,self.age) 
        self.name = None
        self.surname = None
        self.age = None
        self.parts = 0
        self.update_parts_label()

    def unset_pat(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        self.name = None
        self.surname = None
        self.age = None
        self.parts = 0
        self.update_parts_label()
        self.sel_pat = False

    def start_record(self):
        """
        Start recording
        """
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        if not self.running:
            self._type_run_()
            print("Connecting...")
            self.send_start()
            self.running = True
                   
    def stop_record(self):
        """
        Stop recording
        """
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        if self.running:
            print("Shutting down connection") 
            self.send_stop()
            if not self.use_sim: # save raw data from mindflex headset
                save_data(self.data, self.parts)

    # def abort_record(self):
    #     if not self.sel_pat:
    #         self._patient_selection_("not")
    #         return
    #     # debug button
    #     if self.running:
    #         print("Shutting down connection")
    #         self.exper.continue_running = False  # Stop the loop in `read_serial_data()`
    #         self.data = self.exper.stop_serial_data()
    #         self.thread.join(timeout=2)  # Wait for the thread to stop
    #         self.running = False
    #         # self.start_clicked = False
    #         # send TCP signal to stop
    #         self.send_msg(b"stop\n")

    def select_patient(self):
        if self.sel_pat:
            self._patient_selection_()
            return
        elif not self.sel_pat:
            self.parts = 0
            self.name = None
            self.surname = None
            self.age = None
            self.update_parts_label()
            self._type_data_()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='App args')
    # parser.add_argument('--use_lab', required=True, type=bool, help='use labrecorder')
    # parser.add_argument('--use_sim', required=True, type=bool, help='use labrecorder')
    parser.add_argument('use_lab', type=int, help='use labrecorder (1/0)')
    parser.add_argument('use_sim', type=int, help='use simulator (1/0)')
    args = parser.parse_args()

    if args.use_lab == 1:
        use_lab = True
    elif args.use_lab == 0:
        use_lab = False
    else:
        raise TypeError

    if args.use_sim == 1:
        use_sim = True
    elif args.use_sim == 0:
        use_sim = False
    else:
        raise TypeError

    app = MainWindow(use_lab, use_sim)
    app.mainloop()