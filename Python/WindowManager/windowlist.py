import win32gui

def enum_window_titles():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                print(f"{hwnd}: {title}")

    win32gui.EnumWindows(enum_handler, None)

if __name__ == "__main__":
    enum_window_titles()
