import tkinter as tk
import win32gui
import win32con
import win32api
import time
import threading
import psutil

def get_screen_size():
    width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return width, height

def create_overlay_bottom_left(text="🔴 Click to close"):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    #root.attributes("-transparentcolor", "white")
    root.configure(bg="black")

    win_width, win_height = 250, 45
    screen_width, screen_height = get_screen_size()
    x, y = 0, screen_height - win_height
    root.geometry(f"{win_width}x{win_height}+{x}+{y}")
    label = tk.Label(
        root,
        text="Battery: ",
        fg="white",
        bg="black",
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        padx=10
    )
    label.pack(expand=True, fill="both")

    # Update and get HWND
    def update_label():
        battery = psutil.sensors_battery()
        if battery:
            isCharging = 'Ch' if battery.power_plugged else 'NCh'
        label.config(text=f"Battery: {battery.percent}% {isCharging}")
        root.after(60000, update_label)  # Schedule again in 60 seconds

    root.after(10000, update_label)  # Start the timer after 10 seconds
    root.update_idletasks()
    hwnd = win32gui.FindWindow(None, root.title())
    if hwnd == 0:
        hwnd = win32gui.GetForegroundWindow()

    def exit_app():
        print("Overlay closed")
        root.destroy()

    def input_to_stop():
        input("Press Enter in terminal to close the overlay...\n")
        root.after(50, exit_app)
    
    threading.Thread(target=input_to_stop, daemon=True).start()
    
    root.mainloop()

if __name__ == "__main__":
    create_overlay_bottom_left()
