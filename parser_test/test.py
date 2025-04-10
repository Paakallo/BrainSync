import tkinter as tk
from tkinter import messagebox

def open_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Enter Your Information")
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
        name = entry_name.get().strip()
        surname = entry_surname.get().strip()
        age = entry_age.get().strip()
        
        if name and surname and age:
            try:
                int(age)  # Ensure age is a number
                dialog.destroy()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Age must be a number.")
        else:
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")

    # OK Button
    ok_button = tk.Button(dialog, text="OK", command=validate_and_close)
    ok_button.grid(row=3, column=0, columnspan=2, pady=10)

    dialog.transient(root)  # Make the dialog modal
    dialog.grab_set()  # Prevent interaction with the main window
    root.wait_window(dialog)  # Wait for the dialog to close

# Main Application Window
root = tk.Tk()
root.title("Main Window")

# Open Dialog Button
open_dialog_button = tk.Button(root, text="Open Dialog", command=open_dialog)
open_dialog_button.pack(pady=20)

root.mainloop()
