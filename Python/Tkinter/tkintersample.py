import tkinter as tk
from tkinter import ttk

def update_label1():
    text = entry.get()
    label1.config(text=text)

def toggle_label2_color():
    current_color = label2.cget("fg")
    new_color = "green" if current_color == "red" else "red"
    label2.config(fg=new_color)

def exit_app():
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("Tkinter Layout Example")

# Button Style
style = ttk.Style()
style.configure("My.TButton",
    font=("Segoe UI", 12),
    foreground="black",
    background="green",  # won't affect on all OSes unless using themes
    padding=1
)


# Frame for Label 1 and Label 2 side by side
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# Label 1
label1 = tk.Label(top_frame, text="Label 1")
label1.grid(row=0, column=0, padx=10)

# Label 2 with red text
label2 = tk.Label(top_frame, text="Label 2", fg="red")
label2.grid(row=0, column=1, padx=10)

# Entry box for Label 1
entry = tk.Entry(root)
entry.pack(pady=(0, 5))

# Button to update Label 1
button1 = tk.Button(root, text="Update Label 1", command=update_label1)
button1.pack(pady=(0, 10))

# Button to toggle Label 2 color
button2 = tk.Button(root, text="Toggle Label 2 Color", command=toggle_label2_color)
button2.pack(pady=(0, 10))

# Exit button with style
exit_button = ttk.Button(root, text="\u274C Exit", command=exit_app,style="My.TButton")
exit_button.pack(pady=(0, 10))

# Start the main event loop
root.mainloop()
