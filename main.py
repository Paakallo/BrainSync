import tkinter as tk
from tkinter import messagebox
from tkinter import dialog
from brain import Brain
from utils import *
import threading
import socket


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BrainSync")
        self.geometry("400x200")

        self.start_button = tk.Button(self, text="Start", command=self.start_record)
        self.start_button.pack()

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_record)
        self.stop_button.pack()

        self.continue_button = tk.Button(self, text="Continue", command=self.continue_record)
        self.continue_button.pack()

        self.select_button = tk.Button(self, text="Select patient", command=self.select_patient)
        self.select_button.pack()

        self.reset_button = tk.Button(self, text="Reset patient", command=self.res_pat)
        self.reset_button.pack()

        # patient data
        self.name = None
        self.surname = None
        self.age = None

        self.parts = 0
        self.sel_pat = False
        self.exper:Brain = None

        self.data = []
        self.running = False

        self.start_clicked = False # start button

        self.label = tk.Label(self, text=f"{self.parts}")
        self.label.pack()

        if not os.path.exists('data'):
            os.mkdir('data')
        self.lab_recorder = socket.create_connection(("localhost", 22345))
        self.lab_recorder.sendall(b"select all\n")

    def set_lab_dir(self, run = 1):
        participant = f"{self.name}_{self.surname}_{self.age}"
        session = self.parts + 1 # current part maybe 0, but when data is saved, current part is 1
        # run = 1 #TODO: 2 minute runs
        param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:Default}} {{modality:eeg}}\n"
        send_msg = b"filename {template:%p/%s/LabRecorder/%r.xdf} " + param_str.encode()
        self.lab_recorder.sendall(send_msg)

    def update_parts_label(self):
        self.label.config(text=f"Part: {self.parts}")   

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
                        self.sel_existing()
                        self.set_lab_dir()
                        dialog.destroy()
                    else:
                        self.sel_pat = True
                        self.set_lab_dir()
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
    
    def sel_existing(self):
        sel_dialog = tk.Toplevel()
        sel_dialog.title("Enter experiment part")
        sel_dialog.geometry("300x200")

        tk.Label(sel_dialog, text="Part:").grid(row=2, column=0, padx=10, pady=5)
        entry_part = tk.Entry(sel_dialog)
        entry_part.grid(row=0, column=0, columnspan=2, pady=10)

        def confirm():
            try:
                self.parts = int(entry_part.get().strip())
                if self.parts > 3 or self.parts < 0:
                    messagebox.showwarning("Wrong value!")
                else:
                    update_patient(self.name,self.surname,self.age,self.parts)
                    self.update_parts_label()
                    self.sel_pat = True
                    sel_dialog.destroy()
            except:
                messagebox.showwarning("Wrong value!")

        def res_pat():
            reset_patient(self.name,self.surname,self.age)
            self.parts = 0
            self.update_parts_label()
            self.sel_pat = True
            sel_dialog.destroy()

        ok_button = tk.Button(sel_dialog, text="Confirm", command=confirm)
        ok_button.grid(row=3, column=0, columnspan=2, pady=10)

        reset_button = tk.Button(sel_dialog, text="Reset patient", command=res_pat)
        reset_button.grid(row=3, column=1, columnspan=2, pady=10)

        exit_button = tk.Button(sel_dialog, text="Exit", command=sel_dialog.destroy)
        exit_button.grid(row=3, column=2, columnspan=2, pady=10)

        sel_dialog.transient()  # Make the dialog modal
        sel_dialog.grab_set()  # Prevent interaction with the main window
        self.wait_window(sel_dialog)  # Wait for the dialog to close

    def res_pat(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        reset_patient(self.name,self.surname,self.age)
        self.parts = 0
        self.update_parts_label()
    
    def start_record(self):
        """
        Start a series of 2 minute recordings
        """
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        start_time = 0
        run = 0
        self.start_clicked = True
        while self.start_clicked:
            if not self.running:
                print("Connecting...")
                self.exper = Brain(connect2headset())
                # Run `read_serial_data()` in a separate thread
                self.thread = threading.Thread(target=self.exper.read_serial_data, daemon=True)
                self.thread.start()
                self.running = True
                # send TCP signal to start
                self.lab_recorder.sendall(b"start\n")
                # start time measurement
                start_time = time.time()
            else:
                if time.time() - start_time >= 2*60:
                    # stop the loop
                    self.lab_recorder.sendall(b"stop\n")
                    self.exper.continue_running = False  # Stop the loop in `read_serial_data()`
                    self.data = self.exper.get_data()
                    filename = f"{self.name}_{self.surname}_{self.age}"
                    save_data(self.data, self.parts, filename)
                    #run again
                    run += 1
                    self.set_lab_dir(run)
                    self.lab_recorder.sendall(b"start\n")
                    self.exper.continue_running = True
                    start_time = time.time()
                    

    def stop_record(self):
        """
        Stop a series of 2 minute recordings.
        Each series is a single part
        """
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        if self.running and self.start_clicked:
            print("Shutting down connection")
            self.exper.continue_running = False  # Stop the loop in `read_serial_data()`
            self.data = self.exper.stop_serial_data()
            self.thread.join(timeout=2)  # Wait for the thread to stop
            self.running = False
            self.start_clicked = False

            # send TCP signal to stop
            self.lab_recorder.sendall(b"stop\n")

            # save data
            self.parts += 1
            run = 1
            self.update_parts_label()
            save_data(self.data, self.parts)
            self.set_lab_dir(run) # setup for next part

    def continue_record(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        # debug button
        self.parts+=1
        self.update_parts_label()
        # send signal to labrecorder, continue recording
        # self._continue_recording_()

    def select_patient(self):
        if self.sel_pat and self.parts <=2:
            self._patient_selection_()
            return
        elif not self.sel_pat or self.parts == 3:
            self.parts = 0
            self.name = None
            self.surname = None
            self.age = None
            self.update_parts_label()
            self._type_data_()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()