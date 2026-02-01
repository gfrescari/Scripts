from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import win32gui
import win32process
import psutil

app = FastAPI()

def get_visible_windows():
    windows = {}

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    windows[pid] = {
                        "pid": pid,
                        "name": proc.name(),
                        "title": title
                    }
                except psutil.NoSuchProcess:
                    pass

    win32gui.EnumWindows(enum_handler, None)

    # Fallback: foreground window (exclusive fullscreen games)
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            windows[pid] = {
                "pid": pid,
                "name": proc.name(),
                "title": win32gui.GetWindowText(hwnd) or "(Fullscreen / No title)"
            }
        except psutil.NoSuchProcess:
            pass

    return list(windows.values())


@app.get("/api/windows")
def list_windows():
    return get_visible_windows()


@app.post("/api/kill/{pid}")
def kill_process(pid: int):
    try:
        proc = psutil.Process(pid)
        proc.kill()
        return {"status": "killed", "pid": pid}
    except psutil.NoSuchProcess:
        raise HTTPException(404, "Process not found")
    except psutil.AccessDenied:
        raise HTTPException(403, "Access denied (run as admin)")


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Game Process Killer</title>
    <style>
        body { font-family: Arial; background: #111; color: #eee; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; border-bottom: 1px solid #333; }
        button {
            background: #ff4444;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }
        button:hover { background: #ff0000; }
    </style>
</head>
<body>
    <h2>🎮 Running Games & Windows</h2>
    <table id="tbl">
        <thead>
            <tr>
                <th>PID</th>
                <th>Process</th>
                <th>Window Title</th>
                <th></th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>

<script>
async function load() {
    const res = await fetch('/api/windows');
    const data = await res.json();
    const tbody = document.querySelector('tbody');
    tbody.innerHTML = '';
    data.forEach(w => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${w.pid}</td>
            <td>${w.name}</td>
            <td>${w.title}</td>
            <td><button onclick="kill(${w.pid})">❌</button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function kill(pid) {
    if (!confirm('Kill process ' + pid + '?')) return;
    await fetch('/api/kill/' + pid, { method: 'POST' });
    load();
}

load();
setInterval(load, 3000);
</script>
</body>
</html>
"""
