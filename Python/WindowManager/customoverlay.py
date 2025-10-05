import tkinter as tk
import win32gui
import win32con
import win32api
import time
import threading

def make_click_through(hwnd):
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style |= (win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

def remove_click_through(hwnd):
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style &= ~win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

def get_screen_size():
    width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return width, height

def create_overlay_bottom_left(text="🔴 Click to close"):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "white")
    root.configure(bg="white")

    win_width, win_height = 300, 60
    screen_width, screen_height = get_screen_size()
    x, y = 0, screen_height - win_height
    root.geometry(f"{win_width}x{win_height}+{x}+{y}")
    counter = tk.IntVar(value=0)
    label = tk.Label(
        root,
        text=f"{text} ({counter.get()})",
        fg="red",
        bg="white",
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        padx=10
    )
    label.pack(expand=True, fill="both")

    # Update and get HWND
    def update_label():
        counter.set(counter.get() + 1)
        label.config(text=f"{text} ({counter.get()})")
        root.after(30000, update_label)  # Schedule again in 3 minutes

    root.after(30000, update_label)  # Start the timer after 3 minutes
    root.update_idletasks()
    hwnd = win32gui.FindWindow(None, root.title())
    if hwnd == 0:
        hwnd = win32gui.GetForegroundWindow()

    # make_click_through(hwnd) #Uncomment this to make the window click through
    def exit_app():
        print("Overlay closed")
        root.destroy()

    def input_to_stop():
        input("Press Enter in terminal to close the overlay...\n")
        root.after(50, exit_app)
    
    def on_label_click(event):
        # Disable click-through temporarily to let the event go through
        print("on_label_click: clicked")
        # remove_click_through(hwnd) # Use to remove click through
        # print("on_label_click: click-through removed")
        root.after(50, exit_app)  # no lambda
        print("on_label_click: scheduled exit_app")

    label.bind("<Button-1>", on_label_click)
    
    threading.Thread(target=input_to_stop, daemon=True).start()
    
    root.mainloop()

if __name__ == "__main__":
    create_overlay_bottom_left()
