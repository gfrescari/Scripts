import psutil
import pyttsx3
import time
import msvcrt
from datetime import datetime

def batterynotify():
    print("---------------------------------------------")
    print("\033[96mBattery Alarm Check Every 3 Minutes\033[0m")
    print("---------------------------------------------")
    print("Press Delete key to break the loop.")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # 0 for male, 1 for female on many systems
    engine.startLoop(False)	# important in loop
    while True:
        battery = psutil.sensors_battery()
        if battery:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            isCharging = 'Charging' if battery.power_plugged else 'Not Charged'
            print(f"\rBattery: {battery.percent}% {isCharging}", end="")
            if battery.percent > 90:
                print(f"\nBattery percentage: {battery.percent}% at {current_time} {isCharging}")
                for i in range(3):
                    engine.say(f"Battery almost full at {battery.percent}%")
                    engine.iterate()	# Use iteration and not RunAndWait so it can run in loop
                    time.sleep(3)	# Must have delay or iterate will only process once
            elif battery.percent < 25:
                print(f"\nBattery percentage: {battery.percent}% at {current_time} {isCharging}")
                for x in range(3):
                    engine.say(f"Battery low at {battery.percent}%")
                    engine.iterate()
                    time.sleep(3)
            elif battery.percent > 47 and battery.percent < 53:
                print(f"\nBattery percentage: {battery.percent}% at {current_time} {isCharging}")
                for x in range(3):
                    engine.say(f"Battery is at {battery.percent}%")
                    engine.iterate()
                    time.sleep(3)
        else:
            print(f"Battery info not available")
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Delete key (might differ on some terminals)
                print("\nDelete key pressed. Exiting loop.")
                break
            else:
                print(f"Key pressed: {key}")
        time.sleep(3 * 60)

if __name__ == "__main__":
    batterynotify()
