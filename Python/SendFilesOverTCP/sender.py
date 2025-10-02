#!/usr/bin/env python3
import socket
import os
import argparse
import struct
import hashlib

CHUNK_SIZE = 64 * 1024  # 64KB


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def send_file(host, port, filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"Connecting to {host}:{port}")
    print(f"Sending file: {filename} ({filesize:,} bytes)")

    # Create socket and connect
    with socket.create_connection((host, port)) as sock:
        # Send metadata:
        filename_bytes = filename.encode("utf-8")
        sock.sendall(struct.pack("!H", len(filename_bytes)))  # 2 bytes: filename length
        sock.sendall(filename_bytes)                          # filename
        sock.sendall(struct.pack("!Q", filesize))             # 8 bytes: filesize

        # Send file in chunks
        sent = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                print(f"\rSent {sent:,}/{filesize:,} bytes ({(sent/filesize)*100:.1f}%)", end='', flush=True)

        print("\nFile sent successfully.")


def main():
    parser = argparse.ArgumentParser(description="Send a file over TCP with filename and size.")
    parser.add_argument("file", help="Path to file to send")
    parser.add_argument("--host", required=True, help="Receiver IP or hostname")
    parser.add_argument("--port", type=int, required=True, help="Receiver port")
    parser.add_argument("--verify", action="store_true", help="Print SHA-256 of file before sending")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print("File not found:", args.file)
        return

    if args.verify:
        print("SHA-256:", sha256_of_file(args.file))

    send_file(args.host, args.port, args.file)


if __name__ == "__main__":
    main()
# python file_sender.py path/to/your_big_file.iso --host 192.168.1.42 --port 12345 --verify
