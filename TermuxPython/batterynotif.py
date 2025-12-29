#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime

# Android 15 Samsung

def run(cmd):
    return subprocess.check_output(cmd, shell=True).decode().strip()

# Battery info (termux-api)
bat = json.loads(run("termux-battery-status"))

# Smart filtering - only useful temperatures
wanted_keywords = {
    "cpu", "core", "big", "little", "gpu", "mali", "battery",
    "tsens", "pmic", "skin", "quiet", "thermal", "tpu", "npu",
    "aoc", "display"
}

thermal = []
for i in range(60):
    zone_type = run(f"cat /sys/class/thermal/thermal_zone{i}/type 2>/dev/null || true")
    if not zone_type:
        break
    temp_raw = run(f"cat /sys/class/thermal/thermal_zone{i}/temp 2>/dev/null || true")
    if not temp_raw.isdigit():
        continue
    temp_c = int(temp_raw) / 1000

    if any(k in zone_type.lower() for k in wanted_keywords):
        # Clean up the name
        name = zone_type
        name = name.replace("tsens_tz_sensor", "sensor")
        name = name.replace("-thermal", "")
        name = name.replace("cpu", "CPU ")
        name = name.replace("big", "BIG ")
        name = name.replace("little", "LITTLE ")
        name = name.replace("gpu", "GPU")
        name = name.title()
        thermal.append((name, f"{temp_c:.1f}°C"))

# Pretty output
print(f"╔{'═'*50}╗")
print(f"║ Battery & Temperature │ {datetime.now():%Y-%m-%d %H:%M:%S} ║")
print(f"╠{'═'*50}╣\n")

print(f"BATTERY")
print(f"  Level       → {bat['percentage']}%")
print(f"  Status      → {bat['status']}")
print(f"  Health      → {bat['health']}")
print(f"  Temperature → {bat['temperature']:.1f}°C")
print(f"  Current     → {bat.get('current', 0) // 1000} mA\n")

print(f"HOT SPOTS")
for name, temp in thermal:
    icon = "🔥" if float(temp[:-2]) >= 55 else "  "
    print(f"  {icon} {name:<18}: {temp}")

print(f"╚{'═'*50}╝")

# ─── TOAST + PERSISTENT NOTIFICATION WITH CURRENT (mA) ─────────────────────
try:
    # Safely get all temperatures and current
    temps = [float(t[:-2]) for _n, t in thermal if t[:-2].replace('.', '').isdigit()]
    hottest = max(temps) if temps else 0.0

    # Battery current in mA (negative = discharging, positive = charging)
    current_raw = bat.get('current', 0)      # in microamperes (µA)
    current_ma = current_raw // 1000         # convert to mA
    current_sign = "−" if current_ma < 0 else "+" if current_ma > 0 else "±"
    current_display = f"{current_sign}{abs(current_ma)}mA"

    # 1. Silent toast – instant popup, no notification shade clutter
    if bat['percentage'] <= 55 and not bat['status'] == "CHARGING":
        toast_msg = f"🔋 {bat['percentage']}% · {bat['temperature']:.0f}°C · {current_display} · {hottest:.0f}°C"
        subprocess.run(f'termux-toast -s "{toast_msg}"', shell=True, check=False)

    # 2. One persistent notification – updates forever, never duplicates
    status_icon = "🔌" if "CHARGING" in bat['status'] else "⚡" if current_ma > 500 else "🔋"
    subprocess.run([
        "termux-notification", "--id", "battery_monitor",
        "--title", f"{status_icon} {bat['percentage']}% • {bat['status']}",
        "--content", f"{current_display} • Bat {bat['temperature']:.0f}°C • Max {hottest:.0f}°C",
        "--ongoing", "--priority", "low", "--icon", "battery_std"
    ], check=False)

except Exception as e:
    # Never crash – just skip notification if something weird happens
    pass
