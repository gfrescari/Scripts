#!/usr/bin/env python3
import socket
import struct
import os
import argparse
import hashlib

CHUNK_SIZE = 64 * 1024  # 64KB


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def receive_file(port, output_dir="."):
    print(f"Listening on port {port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(("", port))
        server_sock.listen(1)

        conn, addr = server_sock.accept()
        with conn:
            print(f"Connection from {addr[0]}:{addr[1]}")

            # Receive filename length (2 bytes)
            raw = conn.recv(2)
            if len(raw) < 2:
                raise RuntimeError("Connection closed before receiving filename length.")
            (name_len,) = struct.unpack("!H", raw)

            # Receive filename
            filename = conn.recv(name_len).decode("utf-8")
            print(f"Receiving file: {filename}")

            # Receive filesize (8 bytes)
            raw = conn.recv(8)
            if len(raw) < 8:
                raise RuntimeError("Connection closed before receiving filesize.")
            (filesize,) = struct.unpack("!Q", raw)
            print(f"File size: {filesize:,} bytes")

            # Prepare output path
            out_path = os.path.join(output_dir, filename)
            received = 0
            with open(out_path, "wb") as f:
                while received < filesize:
                    chunk = conn.recv(min(CHUNK_SIZE, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    print(f"\rReceived {received:,}/{filesize:,} bytes ({(received/filesize)*100:.1f}%)", end='', flush=True)

            print(f"\nFile saved to: {out_path}")
            print("SHA-256:", sha256_of_file(out_path))


def main():
    parser = argparse.ArgumentParser(description="Receive a file over TCP and save it.")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    parser.add_argument("--output-dir", default=".", help="Directory to save received files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    receive_file(args.port, args.output_dir)


if __name__ == "__main__":
    main()
