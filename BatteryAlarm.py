import psutil
import pyttsx3
import time
from datetime import datetime

def batterynotify():
    print("---------------------------------------------")
    print("\033[96mBattery Alarm Check Every 5 Minutes\033[0m")
    print("---------------------------------------------")
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
            if battery.percent > 90:
                print(f"Battery percentage: {battery.percent}% at {current_time} {isCharging}")
                for i in range(3):
                    engine.say(f"Battery almost full at {battery.percent}%")
                    engine.iterate()	# Use iteration and not RunAndWait so it can run in loop
                    time.sleep(3)	# Must have delay or iterate will only process once
            elif battery.percent < 25:
                print(f"Battery percentage: {battery.percent}% at {current_time} {isCharging}")
                for x in range(3):
                    engine.say(f"Battery low at {battery.percent}%")
                    engine.iterate()
                    time.sleep(3)
            elif battery.percent > 47 and battery.percent < 53:
                print(f"Battery percentage: {battery.percent}% at {current_time} {isCharging}")
                for x in range(3):
                    engine.say(f"Battery is at {battery.percent}%")
                    engine.iterate()
                    time.sleep(3)
        else:
            print(f"Battery info not available")
        time.sleep(5 * 60)

if __name__ == "__main__":
    batterynotify()
