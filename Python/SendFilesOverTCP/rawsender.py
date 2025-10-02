#!/usr/bin/env python3
"""
send_file_to_nc.py
Usage:
    python send_file_to_nc.py --host RECEIVER_HOST --port 12345 path/to/file
    on netcat server: nc -l -p 12345 > received_filename.bin
Example:
    python send_file_to_nc.py --host 192.168.1.10 --port 12345 myfile.zip
"""

import argparse
import os
import socket
import sys
import hashlib

CHUNK_SIZE = 64 * 1024  # 64 KiB

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

def send_file(host, port, path):
    filesize = os.path.getsize(path)
    print(f"Connecting to {host}:{port} — sending '{path}' ({filesize} bytes)")

    # create connection (wraps getaddrinfo and connect)
    with socket.create_connection((host, port)) as s:
        # Optionally: disable Nagle for lower latency (not usually necessary)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        sent = 0
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                # ensure all bytes in chunk are sent
                view = memoryview(chunk)
                while view:
                    n = s.send(view)
                    if n == 0:
                        raise RuntimeError("socket connection broken")
                    view = view[n:]
                sent += len(chunk)
                # progress
                print(f"\rSent {sent}/{filesize} bytes ({sent*100/filesize:5.1f}%)", end="", flush=True)

        print("\nSend complete. Closing connection.")

def main():
    parser = argparse.ArgumentParser(description="Send a file to an nc listener over TCP.")
    parser.add_argument("file", help="Path to file to send")
    parser.add_argument("--host", required=True, help="Receiver host or IP")
    parser.add_argument("--port", type=int, required=True, help="Receiver port")
    parser.add_argument("--verify", action="store_true", help="Print SHA-256 of file locally (for manual verification)")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print("Error: file not found:", args.file, file=sys.stderr)
        sys.exit(2)

    if args.verify:
        print("SHA-256:", sha256_of_file(args.file))

    try:
        send_file(args.host, args.port, args.file)
    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("\nError during send:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
