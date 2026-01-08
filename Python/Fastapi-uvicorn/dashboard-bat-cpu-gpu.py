import psutil
import wmi
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# pip install fastapi uvicorn psutil wmi

app = FastAPI()
c = wmi.WMI(namespace="root\\OpenHardwareMonitor")

# -------------------
# Helper functions
# -------------------
def get_battery():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent, battery.power_plugged
    return None, None

def get_temperatures():
    cpu_temp = None
    gpu_temp = None
    battery_temp = None

    try:
        # Iterate over all hardware sensors
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
        print("Error reading temps:", e)

    return cpu_temp, gpu_temp, battery_temp

# -------------------
# Web Dashboard
# -------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    battery_percent, plugged = get_battery()
    cpu_temp, gpu_temp, battery_temp = get_temperatures()

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
            </style>
        </head>
        <body>
            <h1>System Dashboard</h1>

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

            <p>Page auto-refreshes every 10 seconds.</p>
        </body>
    </html>
    """
    return html

# -------------------
# Run server
# -------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
