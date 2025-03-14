import tkinter as tk

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

        
        self.parts = 0
        self.sel_pat = False

    def _no_patient_selected_(self):
        self.dialog = tk.Toplevel()
        self.dialog.title("Error")
        self.label = tk.Label(self.dialog, text="Select patient to start recording")
        self.label.pack()

        self.continue_button = tk.Button(
            self.dialog, text="Continue", command=lambda: self.dialog.destroy())
        self.continue_button.pack()

    def _continue_recording_(self):
        self.dialog = tk.Toplevel()
        self.dialog.title("Continue")
        self.label = tk.Label(self.dialog, text="Do you want to continue")
        self.label.pack()

        self.yes_button = tk.Button(
            self.dialog, text="Yes", command=lambda: [self.dialog.destroy(), self.continue_record])
        self.yes_button.pack()

        self.no_button = tk.Button(
            self.dialog, text="No", command=lambda: self.dialog.destroy())
        self.no_button.pack()


    def start_record(self):
        if not self.sel_pat:
            self._no_patient_selected_()
            return
        # send signal to labrecorder, start recording

    def stop_record(self):
        self.parts += 1
        # send signal to labrecorder, stop recording and save files

        self._continue_recording_()

    def continue_record(self):
        pass
        # send signal to labrecorder, continue recording

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()