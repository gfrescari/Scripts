import psutil
import wmi
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import pythoncom
import csv
from collections import deque
import os
import subprocess
import re

# pip install fastapi uvicorn psutil wmi

app = FastAPI()
log_file = r"temperatures.csv"  # path to your HWiNFO CSV
# -------------------
# Helper functions
# -------------------

def getWifi():
    output = subprocess.check_output("ipconfig", text=True)
    pattern = re.compile(r"Wireless LAN adapter Wi-Fi.*?IPv4 Address.*?:\s*([\d.]+)",re.S)
    match = pattern.search(output)
    if match:
        print(f"Wifi Ip Address: {match.group(1)}")

def get_battery():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent, battery.power_plugged
    return None, None

def get_temperatures_wmi():
    pythoncom.CoInitialize()
    cpu_temp = None
    gpu_temp = None
    battery_temp = None

    try:
        # Iterate over all hardware sensors
        c = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
        # print(c.Sensor())
        for sensor in c.Sensor():
            if sensor.SensorType == "Temperature":
                name = sensor.Name.lower()
                if "cpu package" in name:
                    cpu_temp = sensor.Value
                elif "gpu" in name or "nvidia" in name:
                    gpu_temp = sensor.Value
                elif "battery" in name:
                    battery_temp = sensor.Value
    except Exception as e:
        print("Error reading temper:", e)
    finally:
        pythoncom.CoUninitialize()

    return cpu_temp, gpu_temp, battery_temp

def get_temperatures_csv_zip():
    cpu_temp = None
    gpu_temp = None
    battery_temp = None

    with open(log_file, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) < 2:
            print("No sensor data yet")
            return
        header = rows[0]
        last_row = rows[-1]
        # Find CPU/GPU columns (example names; adjust to your CSV)
        for name, value in zip(header, last_row):
            if name=="CPU Core [°C]":
                cpu_temp=value
                # print(f"{name}: {value}°C")
            elif "GPU" in name and "Temp" in name:
                gpu_temp=value
                # print(f"{name}: {value}°C")

    return cpu_temp, gpu_temp, battery_temp
    
def get_latest_row():
    """Read the header and last row from CSV using deque."""
    if not os.path.exists(log_file):
        return None, None

    with open(log_file, newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)  # First row: column names
        except StopIteration:
            return None, None  # Empty file

        last_row = deque(reader, maxlen=1)
        if not last_row:
            return header, None
        return header, last_row[0]

def get_temperatures_csv_deque():
    # This method is more memory efficient

    cpu_temp = None
    gpu_temp = None
    battery_temp = None


    header, last_row = get_latest_row()
    data = dict(zip(header, last_row))
    
    cpu_temp = next((value for name, value in data.items() if "CPU Core [°C]" in name.strip()),None)
    gpu_temp = next((value for name, value in data.items() if "GPU Temperature" in name.strip()),None)

    return cpu_temp, gpu_temp, battery_temp


# -------------------
# Web Dashboard
# -------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    battery_percent, plugged = get_battery()
    cpu_temp, gpu_temp, battery_temp = get_temperatures_csv_deque()
    # Get file size
    if os.path.exists(log_file):
        file_size_bytes = os.path.getsize(log_file)
        file_size_kb = file_size_bytes / 1024
    else:
        file_size_bytes = 0
        file_size_kb = 0

    plugged_status = "Plugged In" if plugged else "On Battery"

    html = f"""
    <html>
        <head>
            <title>System Dashboard</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body {{ font-family: Arial, sans-serif; background: #1e1e1e; color: #fff; text-align:center; }}
                .card {{ background: #2e2e2e; padding: 20px; margin: 20px auto; width: 300px; border-radius: 10px; }}
                h1 {{ color: #00ff00; }}
                .value {{ font-size: 2em; color: #00bfff; }}
                .card-container {{
                    display: flex;           /* Makes children align horizontally */
                    gap: 20px;               /* Space between cards */
                    justify-content: center; /* Center cards horizontally */
                    flex-wrap: wrap;         /* Wrap to next line if window is too small */
                }}

            </style>
        </head>
        <body>
            <h1>System Dashboard</h1>
            <div class="card-container">
                <div class="card">
                    <h2>Battery</h2>
                    <p class="value">{battery_percent if battery_percent is not None else 'N/A'}%</p>
                    <p>Status: {plugged_status}</p>
                    <p>Battery Temp: {battery_temp if battery_temp is not None else 'N/A'} °C</p>
                </div>

                <div class="card">
                    <h2>CPU Temperature</h2>
                    <p class="value">{cpu_temp if cpu_temp is not None else 'N/A'} °C</p>
                </div>

                <div class="card">
                    <h2>GPU Temperature</h2>
                    <p class="value">{gpu_temp if gpu_temp is not None else 'N/A'} °C</p>
                </div>
            </div>
            <p>Page auto-refreshes every 10 seconds. Current file size is {file_size_kb} kb</p>
        </body>
    </html>
    """
    return html

# -------------------
# Run server
# -------------------
if __name__ == "__main__":
    getWifi()
    uvicorn.run(app, host="0.0.0.0", port=8000)
