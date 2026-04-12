import subprocess
import time
import json
from datetime import datetime

DEVICE = "127.0.0.1:5555"

ADB_CHECK_INTERVAL = 60      # seconds
THERMAL_INTERVAL = 20        # seconds
MAIN_LOOP_DELAY = 5          # base loop delay

last_adb_check = 0
last_thermal_check = 0

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except:
        return ""

def adb_connected():
    out = run("adb devices")
    return DEVICE in out and "device" in out

def get_battery():
    try:
        return json.loads(run("termux-battery-status"))
    except:
        return None

def get_thermal():
    return run("/system/bin/dumpsys thermalservice")

print("Starting lightweight monitor...")

while True:
    now = time.time()

    # ─── ADB check (throttled) ───
    if now - last_adb_check > ADB_CHECK_INTERVAL:
        adb_status = adb_connected()
        last_adb_check = now
    else:
        adb_status = None

    # ─── Battery (light call) ───
    bat = get_battery()
    if not bat:
        time.sleep(MAIN_LOOP_DELAY)
        continue

    # ─── Thermal (very throttled) ───
    thermal = None
    if now - last_thermal_check > THERMAL_INTERVAL:
        thermal = get_thermal()
        last_thermal_check = now

    # ─── Extract minimal info ───
    temp = None
    if thermal:
        for line in thermal.splitlines():
            if "Temperature" in line:
                temp = line
                break

    # ─── Console output only (no UI spam) ───
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")

    print(f"Battery: {bat.get('percentage')}% | {bat.get('status')}")
    print(f"Temp: {bat.get('temperature')}°C")

    if temp:
        print(f"Thermal: {temp.strip()}")

    if adb_status is not None:
        print(f"ADB: {'CONNECTED' if adb_status else 'DISCONNECTED'}")

    time.sleep(MAIN_LOOP_DELAY)
