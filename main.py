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

        self.label = tk.Label(self, text="")
        self.label.pack()

        self.start_button = tk.Button(self, text="Start", command=self.start_record)
        self.start_button.pack()

        self.stop_button = tk.Button(self, text="Stop", command=self.stop_record)
        self.stop_button.pack()

        self.continue_button = tk.Button(self, text="Continue", command=self.continue_record)
        self.continue_button.pack()

        self.select_button = tk.Button(self, text="Select patient", command=self.select_patient)
        self.select_button.pack()

        # patient data
        self.name = None
        self.surname = None
        self.age = None

        self.parts = 0
        self.sel_pat = False
        self.exper:Brain = None

        self.data = []
        self.running = False

        self.s = socket.create_connection(("localhost", 22345))


        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('patients.json'):
            os.mkdir('patients.json')

    def _patient_selection_(self, text=''):
        self.dialog = tk.Toplevel()
        self.dialog.title("Patient select")
        self.label = tk.Label(self.dialog, text=f"Patient {text} selected")
        self.label.pack()

        self.continue_button = tk.Button(
            self.dialog, text="Continue", command=lambda: self.dialog.destroy())
        self.continue_button.pack()

    # def _continue_recording_(self):
    #     self.dialog = tk.Toplevel()
    #     self.dialog.title("Continue")
    #     self.label = tk.Label(self.dialog, text="Do you want to continue")
    #     self.label.pack()

    #     self.yes_button = tk.Button(
    #         self.dialog, text="Yes", command=lambda: [self.dialog.destroy(), self.continue_record])
    #     self.yes_button.pack()

    #     self.no_button = tk.Button(
    #         self.dialog, text="No", command=lambda: self.dialog.destroy())
    #     self.no_button.pack()

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
                        messagebox.showwarning("Existing record", "Patient already exists")
                        #TODO: select exisiting patient
                    else:
                        self.sel_pat = True
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
    

    def start_record(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        if not self.running:
            print("Connecting...")
            self.exper = Brain(connect2headset())

            # Run `read_serial_data()` in a separate thread
            self.thread = threading.Thread(target=self.exper.read_serial_data, daemon=True)
            self.thread.start()
            self.running = True

            # send TCP signal to start

        

    def stop_record(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        if self.running:
            print("Shutting down connection")
            self.exper.continue_running = False  # Stop the loop in `read_serial_data()`
            self.thread.join(timeout=2)  # Wait for the thread to stop
            self.data = self.exper.stop_serial_data()
            self.running = False

            # send TCP signal to stop

            # save data
            self.parts += 1
            save_data(self.data, self.parts)



    def continue_record(self):
        if not self.sel_pat:
            self._patient_selection_("not")
            return
        
        # send signal to labrecorder, continue recording
        # self._continue_recording_()

    def select_patient(self):
        if self.sel_pat:
            self._patient_selection_()
            return
        
        self._type_data_()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()