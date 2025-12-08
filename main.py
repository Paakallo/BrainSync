import subprocess
import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog
from tkinter import ttk
from brain import Brain
from utils import *
from gen_data import SignalGen
import threading
import socket
import argparse
import os
import time

# Import the processing module
import sync_post_process

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
        self.COM_port = None

        # Ensure the data folder exists
        if not os.path.exists('data'):
            os.mkdir('data')

        if self.use_lab:
            try:
                self.lab_recorder = socket.create_connection(("localhost", 22345))
                self.lab_recorder.sendall(b"select all\n")
            except ConnectionRefusedError:
                messagebox.showerror("Error", "Could not connect to LabRecorder (localhost:22345)")

        if self.use_sim:
            self.exper = SignalGen(1, 256, self.lab_recorder)

        # ================= GUI LAYOUT =================
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Section 1: Patient Management ---
        patient_frame = ttk.LabelFrame(main_frame, text="Patient Management", padding="10")
        patient_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        main_frame.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(patient_frame, text="No Patient Selected", font=("Helvetica", 12, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self.select_button = ttk.Button(patient_frame, text="Select / New Patient", command=self.select_patient)
        self.select_button.grid(row=1, column=0, padx=5, sticky="ew")
        
        self.unset_button = ttk.Button(patient_frame, text="Unset Patient", command=self.unset_pat)
        self.unset_button.grid(row=1, column=1, padx=5, sticky="ew")
        patient_frame.columnconfigure(0, weight=1)
        patient_frame.columnconfigure(1, weight=1)

        # --- Section 2: Configuration ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        ttk.Label(config_frame, text="COM Port:").grid(row=0, column=0, sticky="w", pady=5)
        self.port_combo = ttk.Combobox(config_frame, state="readonly", values=[i for i in range(1, 11)])
        self.port_combo.grid(row=0, column=1, padx=10, sticky="ew")
        self.confirm_port_button = ttk.Button(config_frame, text="Set Port", command=self.set_port)
        self.confirm_port_button.grid(row=0, column=2, padx=5)

        ttk.Label(config_frame, text="Session Part:").grid(row=1, column=0, sticky="w", pady=5)
        self.parts_combo = ttk.Combobox(config_frame, state="readonly", values=[i for i in range(1, 8)])
        self.parts_combo.grid(row=1, column=1, padx=10, sticky="ew")
        self.confirm_parts_button = ttk.Button(config_frame, text="Set Part", command=self.set_selected_part)
        self.confirm_parts_button.grid(row=1, column=2, padx=5)

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
        main_frame.rowconfigure(3, weight=1)

        self.lbl_part_status = ttk.Label(status_frame, text="Current Part: 0")
        self.lbl_part_status.grid(row=0, column=0, sticky="w", padx=10, pady=2)
        self.lbl_run_status = ttk.Label(status_frame, text="Current Run: 0")
        self.lbl_run_status.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.lbl_active_status = ttk.Label(status_frame, text="Is Running: False", foreground="red")
        self.lbl_active_status.grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.port_info = ttk.Label(status_frame, text="COM Port: Not Set")
        self.port_info.grid(row=3, column=0, sticky="w", padx=10, pady=2)
        self.lbl_sync_status = ttk.Label(status_frame, text="Sync Status: Idle")
        self.lbl_sync_status.grid(row=4, column=0, sticky="w", padx=10, pady=2)

    # ================= LOGIC =================

    def toggle_ui_state(self, is_recording):
        """
        Disables or enables UI components based on recording state.
        If is_recording is True, everything except STOP is disabled.
        """
        state = "disabled" if is_recording else "normal"
        
        # Disable/Enable Patient Controls
        self.select_button.config(state=state)
        self.unset_button.config(state=state)
        
        # Disable/Enable Configuration
        self.port_combo.config(state=state)
        self.confirm_port_button.config(state=state)
        self.parts_combo.config(state=state)
        self.confirm_parts_button.config(state=state)
        self.rem_part_button.config(state=state)
        
        # Disable/Enable Start Button
        self.start_button.config(state=state)

    def send_msg(self, msg: str):
        if self.use_lab and self.lab_recorder:
            try:
                self.lab_recorder.sendall(msg)
            except Exception as e:
                print(f"Error sending to LabRecorder: {e}")

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

    def get_participant_str(self):
        return f"{self.name}_{self.surname}_{self.age}"

    def set_lab_dir(self, run=1):
        if not self.name: 
            return
        participant = self.get_participant_str()
        session = self.parts
        # Template: %p = participant, %s = session, %r = run
        param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:{run}}} {{modality:eeg}} {{block:{run}}}\n"
        # LabRecorder stores in: Root / Participant / Session / LabRecorder / run.xdf
        send_msg = b"filename {template:%p/%s/labrecorder/%b.xdf} " + param_str.encode()
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

    # Messages
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
                    # Note: assuming add_patient is in utils
                    try:
                        exists = not add_patient(self.name, self.surname, self.age)
                    except NameError:
                        exists = False 

                    if exists:
                        self._sel_existing_()
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
        try:
            reset_patient(self.name, self.surname, self.age)
        except NameError: pass
        self.parts = 0
        self.update_parts_label()
    
    def rem_part(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        try:
            remove_part(self.name, self.surname, self.age, self.parts)
        except NameError: pass
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

    # --- Recording & Processing Logic ---
    
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

    def start_record(self):
        if not self.sel_pat:
            messagebox.showwarning("Required", "Please select a patient first.")
            return

        if not self.running:
            if self._type_run_():
                print("Connecting...")
                self.send_start()
                self.running = True
                
                # --- Lock the UI ---
                self.toggle_ui_state(True)
                
                self.update_parts_label()
                self.lbl_sync_status.config(text="Sync Status: Recording...")
                   
    def stop_record(self):
        if not self.sel_pat:
            return

        if self.running:
            print("Shutting down connection") 
            self.send_stop()
            
            if not self.use_sim:
                try:
                    save_data(self.data, self.parts)
                except NameError: pass 

            self.update_parts_label()
            
            # --- Unlock the UI ---
            self.toggle_ui_state(False)
            
            # Trigger Post-Processing
            if self.use_lab:
                threading.Thread(target=self._wait_and_process, daemon=True).start()

    def _wait_and_process(self):
        """
        Calculates expected file path in the DATA folder, waits for it, and runs sync.
        """
        self.lbl_sync_status.config(text="Sync Status: Waiting for file...", foreground="orange")
        
        part_str = self.get_participant_str()
        expected_path = os.path.join(
            os.getcwd(), 
            "data", 
            part_str, 
            str(self.parts), 
            "labrecorder", 
            f"{self.run_no}.xdf"
        )
        print(f"Looking for: {expected_path}")

        # Wait loop (max 10 seconds)
        found = False
        for _ in range(20):
            if os.path.exists(expected_path):
                found = True
                break
            time.sleep(0.5)

        if found:
            self.lbl_sync_status.config(text="Sync Status: Processing...", foreground="blue")
            try:
                # Call the function from the other file
                csv_out = sync_post_process.process_and_save(expected_path)
                if csv_out:
                    self.lbl_sync_status.config(text="Sync Status: Saved CSV", foreground="green")
                else:
                    self.lbl_sync_status.config(text="Sync Status: Error in Sync", foreground="red")
            except Exception as e:
                print(f"Sync error: {e}")
                self.lbl_sync_status.config(text="Sync Status: Exception", foreground="red")
        else:
            print("File not found (LabRecorder path mismatch?)")
            self.lbl_sync_status.config(text="Sync Status: File Not Found", foreground="red")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='App args')
    parser.add_argument('use_lab', type=int, help='use labrecorder (1/0)')
    parser.add_argument('use_sim', type=int, help='use simulator (1/0)')
    args = parser.parse_args()

    use_lab = bool(args.use_lab)
    use_sim = bool(args.use_sim)
    lab_proc = None

    if use_lab:
        try:
            print("Launching LabRecorder...")
            lab_proc = subprocess.Popen(["LabRecorder"])
            time.sleep(2) 
        except FileNotFoundError:
            print("Warning: 'LabRecorder' command not found. Please start it manually.")
        except Exception as e:
            print(f"Error starting LabRecorder: {e}")

    app = MainWindow(use_lab, use_sim)
    app.mainloop()

    if lab_proc:
        print("Terminating LabRecorder...")
        lab_proc.terminate()
        try:
            lab_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print("Force killing LabRecorder...")
            lab_proc.kill()