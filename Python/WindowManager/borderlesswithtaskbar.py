import time
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes

def force_borderless(window_title, width=win32api.GetSystemMetrics(win32con.SM_CXSCREEN), height=win32api.GetSystemMetrics(win32con.SM_CYSCREEN), x=0, y=0):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Window with title '{window_title}' not found.")
        return False
    
     # Get work area (excludes taskbar area)
    work_area = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(win32con.SPI_GETWORKAREA, 0, ctypes.byref(work_area), 0)
    
    x = work_area.left
    y = work_area.top
    width = work_area.right - work_area.left
    height = work_area.bottom - work_area.top
    
    # Remove window styles: caption, thick frame, minimize/maximize buttons
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    # Remove extended styles that may add borders or shadows
    exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    exstyle &= ~(win32con.WS_EX_DLGMODALFRAME | win32con.WS_EX_CLIENTEDGE | win32con.WS_EX_STATICEDGE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle)

    # Apply the style changes (forces the window to redraw)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, x, y, width, height,
                          win32con.SWP_FRAMECHANGED | win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)

    print(f"Window '{window_title}' forced to borderless at ({x},{y},{width}x{height})")
    return True


if __name__ == "__main__":
    # Example usage:

    # Screen resolution (you can fetch this programmatically)
    #screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    #screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    # Replace this with your game window's title exactly
    game_window_title = "Snipping Tool"

    # Wait a few seconds to allow you to launch the game
    print("Waiting 5 seconds. Launch the game now.")
    time.sleep(5)

    success = force_borderless(game_window_title)

    if not success:
        print("Could not find the game window. Make sure it is running and visible.")
