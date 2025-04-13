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

        self.rem_part_button = tk.Button(self, text="Remove part", command=self.rem_part)
        self.rem_part_button.pack()

        self.remove_button = tk.Button(self, text="Remove patient", command=self.rem_pat)
        self.remove_button.pack()

        self.unset_button = tk.Button(self, text="Unset patient", command=self.unset_pat)
        self.unset_button.pack()

        # Single-selection Listbox for choosing a part
        self.parts_listbox = tk.Listbox(self, selectmode=tk.SINGLE, height=3, exportselection=False)
        for i in range(1,8):
            self.parts_listbox.insert(tk.END, i)
        self.parts_listbox.pack()
        # Button to assign selected part to self.parts
        self.confirm_parts_button = tk.Button(self, text="Set Selected Part", command=self.set_selected_part)
        self.confirm_parts_button.pack()

        # Single-selection Listbox for choosing a part
        self.port_listbox = tk.Listbox(self, selectmode=tk.SINGLE, height=3, exportselection=False)
        self.port_listbox.insert(0, 5)
        self.port_listbox.insert(1, 6)
        self.port_listbox.pack()
        # Button to assign selected part to self.parts
        self.confirm_port_button = tk.Button(self, text="Set COM Port", command=self.set_port)
        self.confirm_port_button.pack()



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

        # display COM port
        self.port_info = tk.Label(self, text=f"COM{self.COM_port}")
        self.port_info.pack()

        if not os.path.exists('data'):
            os.mkdir('data')
        self.lab_recorder = socket.create_connection(("localhost", 22345))
        self.lab_recorder.sendall(b"select all\n")

    def set_port(self):
        selected = self.port_listbox.curselection()
        if selected:
            self.COM_port = selected[0] + 5 # temporary fix 
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

    def set_lab_dir(self,run = 1):
        participant = f"{self.name}_{self.surname}_{self.age}"
        # session = self.parts + 1 # current part maybe 0, but when data is saved, current part is 1
        session = self.parts
        param_str = f"{{run:{run}}} {{participant:{participant}}} {{session:{session}}} {{task:Default}} {{modality:eeg}}\n"
        send_msg = b"filename {template:%p/%s/LabRecorder/%r.xdf} " + param_str.encode()
        self.lab_recorder.sendall(send_msg)

    def update_parts_label(self):
        self.label.config(text=f"Current Part: {self.parts} \nCurrent Run:{self.run_no}")   
        self.info_label.config(text=f"{self.name}_{self.surname}_{self.age}")        

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
        
        self.start_clicked = True
        while self.start_clicked:

            self._type_run_()
            if not self.running:
                print("Connecting...")
                self.exper = Brain(connect2headset(f"COM{self.COM_port}"))
                # Run `read_serial_data()` in a separate thread
                self.thread = threading.Thread(target=self.exper.read_serial_data, daemon=True)
                self.thread.start()
                self.running = True
                # send TCP signal to start
                self.lab_recorder.sendall(b"start\n")
                   
    def stop_record(self):
        """
        Stop recording
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
            #self.parts += 1
            save_data(self.data, self.parts)
            #self.parts += 1
            #run = 1
            # self.update_parts_label()
            # self.set_lab_dir(self.run_no) # setup for next part

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
    app = MainWindow()
    app.mainloop()