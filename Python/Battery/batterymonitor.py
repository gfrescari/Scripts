import psutil
import time
import sys
from datetime import datetime

def batterymonitor():
    while True:
        battery = psutil.sensors_battery()
        if battery:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            isCharging = 'Charging' if battery.power_plugged else 'Not Charged'
            print(f"\033[1mTime: {current_time}")
            sys.stdout.flush()
            print(f"Battery: {battery.percent}% {isCharging}")
            sys.stdout.flush()
            
        else:
            print(f"Battery info not available")
        time.sleep(60)
        for _ in range(2):
            sys.stdout.write("\033[F")
            sys.stdout.flush()
            sys.stdout.write("\033[K")
            sys.stdout.flush()
            
if __name__ == "__main__":
    batterymonitor()
