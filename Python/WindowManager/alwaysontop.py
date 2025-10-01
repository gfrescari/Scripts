import win32gui
import win32con
import time

def set_always_on_top(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Window with title '{window_title}' not found.")
        return False
    
    # Set the window as topmost without changing size or position
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    print(f"Window '{window_title}' set to always on top.")
    return True

if __name__ == "__main__":
    print("Waiting 5 seconds. Launch your game window.")
    time.sleep(5)
    set_always_on_top("Your Game Window Title Here")
