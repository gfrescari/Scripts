from win10toast import ToastNotifier
import time
import msvcrt

def showToast():
    toaster = ToastNotifier()
    toaster.show_toast(
        "Notification Title",
        "This is the body of the toast notification.",
        duration=5,  # seconds
        threaded=True,  # So it doesn't block your script
        icon_path=None  # You can provide a .ico file here
    )
    
def isDelete():
    if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Delete key (might differ on some terminals)
                print("\nDelete key pressed. Exiting loop.")
                return True
            else:
                print(f"Key pressed: {key}")
                return False

if __name__ == "__main__":
    while True:
        showToast()
        if isDelete():
            break
        time.sleep(10)
