#!/data/data/com.termux/files/usr/bin/python
# File: ~/battery_thermal_status.py
# Usage: python ~/battery_thermal_status.py
#        or alias bt='python ~/battery_thermal_status.py'

import subprocess
import re
import sys
import time
import json
from datetime import datetime

# Colors (ANSI escape codes)
RED    = '\033[0;31m'
GREEN  = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN   = '\033[0;36m'
NC     = '\033[0m'

# ADB connection settings
DEVICE = "127.0.0.1:5555"
MAX_TRIES = 3
SLEEP_BETWEEN = 2

def run_command(cmd, check=True):
    """Run shell command and return stripped output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""

def check_adb_connection():
    """Check if ADB is connected, try to reconnect if not"""
    print(f"{CYAN}Checking ADB connection...{NC}")

    # Check current devices
    devices = run_command("adb devices")
    if f"{DEVICE}\tdevice" in devices:
        print(f"  {GREEN}Already connected ✓{NC}")
        return True

    print(f"  {YELLOW}No connection found — trying to connect...{NC}")

    for attempt in range(1, MAX_TRIES + 1):
        print(f"  Attempt {attempt}/{MAX_TRIES}... ", end="", flush=True)
        run_command(f"adb connect {DEVICE}", check=False)
        time.sleep(SLEEP_BETWEEN)

        devices = run_command("adb devices")
        if f"{DEVICE}\tdevice" in devices:
            print(f"{GREEN}Success! ✓{NC}")
            return True
        else:
            print(f"{RED}Failed{NC}")

    print(f"\n{RED}Could not connect after {MAX_TRIES} attempts.{NC}")
    print("Please make sure:")
    print("  • Wireless debugging is ON")
    print("  • You previously ran 'adb tcpip 5555'")
    print("  • Wi-Fi is active on the tablet")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# Main script starts here
# ──────────────────────────────────────────────────────────────
check_adb_connection()

print()
print(f"{CYAN}┌────────────────────────────────────────────────────┐{NC}")
print(f"{CYAN}│    Battery & Thermal Status  ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) │{NC}")
print(f"{CYAN}└────────────────────────────────────────────────────┘{NC}")
print()

# ──────────────────────────────────────────────────────────────
# Battery Information
# ──────────────────────────────────────────────────────────────
# Battery info (termux-api)                                                                                                                                                     
bat = json.loads(run_command("termux-battery-status"))

print(f"{YELLOW}Battery Information:{NC}")
print(f"  Level       → {bat['percentage']}%")
print(f"  Status      → {bat['status']}")                                                                                                                                             
print(f"  Health      → {bat['health']}")
print(f"  Temperature → {bat['temperature']:.1f}°C")
print(f"  Current     → {bat.get('current', 0) // 1000} mA\n")


# ──────────────────────────────────────────────────────────────
# Thermal Information
# ──────────────────────────────────────────────────────────────
print(f"{YELLOW}Thermal Information:{NC}")

thermal_raw = run_command("/system/bin/dumpsys thermalservice | awk '/Current temperatures from HAL:/{p=1} p && /Temperature/{print} p && /Current cooling devices from HAL:/{p=0}'")

if thermal_raw:
    cpu_matches = re.findall(r'Temperature{mValue=([\d.]+).*?(cpu|soc|ap|tsens|cluster).*?', thermal_raw, re.IGNORECASE)
    cpu_temp = cpu_matches[0][0] if cpu_matches else None

    gpu_matches = re.findall(r'Temperature{mValue=([\d.]+).*?(GPU|MALI|adreno).*?', thermal_raw, re.IGNORECASE)
    gpu_temp = gpu_matches[0][0] if gpu_matches else None

    if cpu_temp:
        print(f"  CPU / SoC:              {GREEN}{cpu_temp} °C{NC}")
    else:
        print(f"  CPU / SoC:              {YELLOW}not detected{NC}")

    if gpu_temp:
        print(f"  GPU:                    {GREEN}{gpu_temp} °C{NC}")
    else:
        print(f"  GPU:                    {YELLOW}not detected{NC}")

    print()
    print(f"{CYAN}First few temperature readings:{NC}")
    temp_lines = [line for line in thermal_raw.splitlines() if 'Temperature' in line][:5]
    for line in temp_lines:
        print("  " + line.strip())
else:
    print(f"  {RED}thermalservice not responding{NC}")
    print("  Try manually: /system/bin/dumpsys thermalservice")

print()
print(f"{CYAN}──────────────────────────────────────────────────────{NC}")

# ─── TOAST + PERSISTENT NOTIFICATION WITH CURRENT (mA) ─────────────────────
try:
    # Battery current in mA (negative = discharging, positive = charging)
    current_raw = bat.get('current', 0)      # in microamperes (µA)
    current_ma = current_raw // 1000         # convert to mA
    current_sign = "−" if current_ma < 0 else "+" if current_ma > 0 else "±"
    current_display = f"{current_sign}{abs(current_ma)}mA"

    # 1. Silent toast – instant popup, no notification shade clutter

    if bat['percentage'] <= 55 and not bat['status'] == "CHARGING":

        toast_msg = f"🔋 {bat['percentage']}% · {bat['temperature']:.0f}°C · {current_display} · CPU {float(cpu_temp):.0f} °C"

        subprocess.run(f'termux-toast -s "{toast_msg}"', shell=True, check=False)
        for i in range(3):
            run_command("play -n synth 0.5 sine 1000 >/dev/null 2>&1")
            time.sleep(0.6)

    if bat['percentage'] >= 90 and bat['status'] == "CHARGING":

        toast_msg = f"🔋 {bat['percentage']}% · {bat['temperature']:.0f}°C · {current_display} · CPU {float(cpu_temp):.0f} °C"

        subprocess.run(f'termux-toast -s "{toast_msg}"', shell=True, check=False)
        for i in range(3):
            run_command("play -n synth 0.5 sine 1000 >/dev/null 2>&1")
            time.sleep(0.6)

     # 2. One persistent notification – updates forever, never duplicates

    status_icon = "🔌" if "CHARGING" in bat['status'] else "⚡" if current_ma > 500 else "🔋"

    subprocess.run([

        "termux-notification", "--id", "battery_monitor",
                                                                                                                                                                                              "--title", f"{status_icon} {bat['percentage']}% • {bat['status']}",

                                                                                                                                                                                              "--content", f"{current_display} • Bat {bat['temperature']:.0f}°C • CPU {float(cpu_temp):.0f} °C",

        "--ongoing", "--priority", "low", "--icon", "battery_std"

    ], check=False)


except Exception as e:
    # Never crash – just skip notification if something weird happens

    pass
