import socket
import subprocess

ANDROID_IP = '192.168.x.x'  # Replace with your Android IP
ANDROID_PORT = <port must be the same as device B>

def send_bat_output():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ANDROID_IP, ANDROID_PORT))
        process = subprocess.Popen(['cmd.exe', '/c', 'batterymonitor.bat'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,bufsize=1)

        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            s.sendall(line.encode())

        process.stdout.close()
        process.wait()

if __name__ == '__main__':
    send_bat_output()
