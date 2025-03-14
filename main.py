import tkinter as tk

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BrainSync")
        self.geometry("400x200")

        self.label = tk.Label(self, text="")
        self.label.pack()

        self.introduction_button = tk.Button(self, text="Start", command=self.show_introduction)
        self.introduction_button.pack()



if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()