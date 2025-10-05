import time
import win32gui
import win32con
import win32api

def force_borderless_cover_taskbar(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Window with title '{window_title}' not found.")
        return False

    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # Set WS_POPUP style removes borders and disables taskbar button
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, win32con.WS_POPUP)

    # Make the window topmost and resize to full screen (including taskbar area)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, screen_width, screen_height,
                          win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)

    print(f"Window '{window_title}' forced borderless fullscreen covering taskbar.")
    return True

if __name__ == "__main__":
    print("Waiting 5 seconds. Launch your game window.")
    time.sleep(5)
    force_borderless_cover_taskbar("Your Game Window Title Here")
