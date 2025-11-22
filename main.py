import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog
from tkinter import ttk  # Import themed tkinter
from brain import Brain
from utils import *
from gen_data import SignalGen
import threading
import socket
import argparse
import os

# Tutaj labrecorder frontend

class MainWindow(tk.Tk):
    def __init__(self, use_lab: bool, use_sim: bool):
        super().__init__()
        self.title("BrainSync Recorder")
        self.geometry("600x650") 
        style = ttk.Style()
        style.theme_use('clam')

        # --- Data & State ---
        self.use_lab = use_lab
        self.use_sim = use_sim
        self.lab_recorder = None
        
        self.name = None
        self.surname = None
        self.age = None
        self.parts = 0
        self.run_no = 0
        self.sel_pat = False
        self.exper: Brain = None
        self.data = []
        self.running = False
        self.start_clicked = False 
        self.COM_port = None

        if not os.path.exists('data'):
            os.mkdir('data')

        if self.use_lab:
            try:
                self.lab_recorder = socket.create_connection(("localhost", 22345))
                self.lab_recorder.sendall(b"select all\n")
            except ConnectionRefusedError:
                messagebox.showerror("Error", "Could not connect to LabRecorder (localhost:22345)")

        if self.use_sim:
            self.exper = SignalGen(1, 256, 0, self.lab_recorder)

        # ================= GUI LAYOUT =================

        # Main Container with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Section 1: Patient Management ---
        patient_frame = ttk.LabelFrame(main_frame, text="Patient Management", padding="10")
        patient_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        main_frame.columnconfigure(0, weight=1) # Make column expandable

        # Patient Info Display
        self.info_label = ttk.Label(patient_frame, text="No Patient Selected", font=("Helvetica", 12, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Patient Buttons
        self.select_button = ttk.Button(patient_frame, text="Select / New Patient", command=self.select_patient)
        self.select_button.grid(row=1, column=0, padx=5, sticky="ew")
        
        self.unset_button = ttk.Button(patient_frame, text="Unset Patient", command=self.unset_pat)
        self.unset_button.grid(row=1, column=1, padx=5, sticky="ew")

        # Configure grid weights for buttons
        patient_frame.columnconfigure(0, weight=1)
        patient_frame.columnconfigure(1, weight=1)


        # --- Section 2: Configuration (Ports & Parts) ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        # COM Port
        ttk.Label(config_frame, text="COM Port:").grid(row=0, column=0, sticky="w", pady=5)
        self.port_combo = ttk.Combobox(config_frame, state="readonly", values=[i for i in range(1, 11)])
        self.port_combo.grid(row=0, column=1, padx=10, sticky="ew")
        self.confirm_port_button = ttk.Button(config_frame, text="Set Port", command=self.set_port)
        self.confirm_port_button.grid(row=0, column=2, padx=5)

        # Session Part
        ttk.Label(config_frame, text="Session Part:").grid(row=1, column=0, sticky="w", pady=5)
        self.parts_combo = ttk.Combobox(config_frame, state="readonly", values=[i for i in range(1, 8)])
        self.parts_combo.grid(row=1, column=1, padx=10, sticky="ew")
        self.confirm_parts_button = ttk.Button(config_frame, text="Set Part", command=self.set_selected_part)
        self.confirm_parts_button.grid(row=1, column=2, padx=5)

        # Remove Part Button
        self.rem_part_button = ttk.Button(config_frame, text="Remove Last Part", command=self.rem_part)
        self.rem_part_button.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="ew")


        # --- Section 3: Recording Controls ---
        control_frame = ttk.LabelFrame(main_frame, text="Recording Control", padding="10")
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(control_frame, text="START RECORDING", command=self.start_record)
        self.start_button.grid(row=0, column=0, ipady=15, padx=5, sticky="ew")

        self.stop_button = ttk.Button(control_frame, text="STOP", command=self.stop_record)
        self.stop_button.grid(row=0, column=1, ipady=15, padx=5, sticky="ew")


        # --- Section 4: Status Monitor ---
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=3, column=0, sticky="nsew")
        main_frame.rowconfigure(3, weight=1) # Status takes remaining space

        # Use a grid for status labels
        self.lbl_part_status = ttk.Label(status_frame, text="Current Part: 0")
        self.lbl_part_status.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        self.lbl_run_status = ttk.Label(status_frame, text="Current Run: 0")
        self.lbl_run_status.grid(row=1, column=0, sticky="w", padx=10, pady=2)

        self.lbl_active_status = ttk.Label(status_frame, text="Is Running: False", foreground="red")
        self.lbl_active_status.grid(row=2, column=0, sticky="w", padx=10, pady=2)

        self.port_info = ttk.Label(status_frame, text="COM Port: Not Set")
        self.port_info.grid(row=3, column=0, sticky="w", padx=10, pady=2)

    # ================= LOGIC =================

    def send_msg(self, msg: str):
        if self.use_lab and self.lab_recorder:
            self.lab_recorder.sendall(msg)

    def send_start(self):
        if self.use_sim:
            self.exper.sendData("1_Hz", "256_Hz")
        else:
            try:
                self.exper = Brain(connect2headset(f"COM{self.COM_port}"))
                self.thread = threading.Thread(target=self.exper.read_serial_data, daemon=True)
                self.thread.start()
                self.send_msg(b"start\n")
            except:
                self._wrong_port_()

    def send_stop(self):
        if self.use_sim:
            self.exper.running = False
            self.exper.stopData()
        else:
            self.exper.continue_running = False
            self.data = self.exper.stop_serial_data()
            self.send_msg(b"stop\n")
            self.thread.join(timeout=2)
        self.running = False

    def set_selected_part(self):
        val = self.parts_combo.get()
        if val:
            self.parts = int(val)
            self.set_lab_dir()
            self.update_parts_label()
            messagebox.showinfo("Part Set", f"Selected Part: {self.parts}")
        else:
            messagebox.showwarning("No Selection", "Please select a part from the list.")

    def set_lab_dir(self, run=1):
        if not self.name: 
            return
        participant = f"{self.name}_{self.surname}_{self.age}"
        session = self.parts
        param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:Default}} {{modality:eeg}}\n"
        send_msg = b"filename {template:%p/%s/LabRecorder/%r.xdf} " + param_str.encode()
        self.send_msg(send_msg)

    def update_parts_label(self):
        self.lbl_part_status.config(text=f"Current Part: {self.parts}")
        self.lbl_run_status.config(text=f"Current Run: {self.run_no}")
        if self.name:
            pat_text = f"{self.name} {self.surname} ({self.age})"  
        else: 
            pat_text = "No Patient Selected"
        self.info_label.config(text=pat_text)
        self.lbl_active_status.config(text=f"Is Running: {self.running}", foreground="green" if self.running else "red")

    def update_COM_label(self):
        self.port_info.config(text=f"COM Port: COM{self.COM_port}")

    # Messages and warnings
    def _patient_selection_(self, text=''):
        messagebox.showinfo("Selection Info", f"Patient {text} selected.")

    def _type_data_(self):
        dialog = tk.Toplevel()
        dialog.title("New Patient Entry")
        dialog.geometry("350x250")
        
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_name = tk.Entry(dialog)
        entry_name.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Surname:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_surname = tk.Entry(dialog)
        entry_surname.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Age:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        entry_age = tk.Entry(dialog)
        entry_age.grid(row=2, column=1, padx=10, pady=10)

        def validate_and_close():
            self.name = entry_name.get().strip()
            self.surname = entry_surname.get().strip()
            self.age = entry_age.get().strip()
            
            if self.name and self.surname and self.age:
                try:
                    int(self.age)
                    if not add_patient(self.name, self.surname, self.age):
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

        ok_button = ttk.Button(dialog, text="Create Patient", command=validate_and_close)
        ok_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew", padx=20)

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
    def _sel_existing_(self):
        if messagebox.askyesno("Patient Exists", "Patient already exists. Select them?"):
            self.parts = 1
            self.set_lab_dir()
            self.sel_pat = True
            self.update_parts_label()
        else:
            self.name = None
            self.surname = None
            self.age = None

    def _type_run_(self):
        run_input = tk.simpledialog.askinteger("Run Number", f"Current Part: {self.parts}\nEnter Run Number:", parent=self, minvalue=1)
        if run_input is not None:
            self.run_no = run_input
            self.set_lab_dir(self.run_no)
            self.update_parts_label()
            return True
        return False

    def _wrong_port_(self):
        messagebox.showerror("Connection Error", f"Could not connect to COM{self.COM_port}")

    # Buttons
    def set_port(self):
        val = self.port_combo.get()
        if val:
            self.COM_port = int(val)
            self.update_COM_label()
        else:
            messagebox.showwarning("No Selection", "Please select a COM port from the list.")

    def res_pat(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        reset_patient(self.name, self.surname, self.age)
        self.parts = 0
        self.update_parts_label()
    
    def rem_part(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        remove_part(self.name, self.surname, self.age, self.parts)
        if self.parts > 0:
            self.parts -= 1
        else:
            self.parts += 1
        self.update_parts_label()

    def unset_pat(self):
        self.name = None
        self.surname = None
        self.age = None
        self.parts = 0
        self.sel_pat = False
        self.update_parts_label()

    def start_record(self):
        if not self.sel_pat:
            messagebox.showwarning("Required", "Please select a patient first.")
            return

        if not self.running:
            if self._type_run_(): # Only start if user entered a run number
                print("Connecting...")
                self.send_start()
                self.running = True
                self.update_parts_label()
                   
    def stop_record(self):
        if not self.sel_pat:
            return

        if self.running:
            print("Shutting down connection") 
            self.send_stop()
            if not self.use_sim:
                save_data(self.data, self.parts)
            self.update_parts_label()

    def select_patient(self):
        if self.sel_pat:
            messagebox.showinfo("Info", "Patient already selected. Unset first to change.")
            return
        
        self.parts = 0
        self.name = None
        self.surname = None
        self.age = None
        self.update_parts_label()
        self._type_data_()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='App args')
    parser.add_argument('use_lab', type=int, help='use labrecorder (1/0)')
    parser.add_argument('use_sim', type=int, help='use simulator (1/0)')
    args = parser.parse_args()

    use_lab = bool(args.use_lab)
    use_sim = bool(args.use_sim)

    app = MainWindow(use_lab, use_sim)
    app.mainloop()