#!/usr/bin/env python3
"""
raw_receiver.py - simple netcat-like TCP receiver that writes raw bytes to a file.

Usage:
    # Save to a file named "received.bin"
    python raw_receiver.py --port 12345 --output received.bin

    # Write to stdout (careful: binary data in terminal)
    python raw_receiver.py --port 12345 --output -

    # Listen on IPv6 as well (optional)
    python raw_receiver.py --port 12345 --host :: --output received.bin

Notes:
    - The script accepts one connection, writes all received bytes, then exits.
    - It streams in chunks and never buffers the entire file in memory (safe for multi-GB files).
    - If the output file exists it will be overwritten by default. Use --append to append.
"""
import socket
import argparse
import sys
import os
import signal

CHUNK_SIZE = 64 * 1024  # 64 KiB


def handle_sigint(signum, frame):
    print("\nInterrupted. Exiting.", file=sys.stderr)
    sys.exit(1)


def receive_raw(port, host, out_path, append=False, quiet=False):
    signal.signal(signal.SIGINT, handle_sigint)

    family = socket.AF_INET6 if ':' in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as server:
        # allow quick reuse
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((host, port))
        except Exception as e:
            print(f"Failed to bind {host}:{port} — {e}", file=sys.stderr)
            sys.exit(2)

        server.listen(1)
        if not quiet:
            print(f"Listening on {host}:{port} ... (waiting for one connection)")

        conn, addr = server.accept()
        with conn:
            if not quiet:
                print(f"Connection from {addr[0]}:{addr[1]} -- receiving data...")

            # Open output (handle '-' as stdout)
            mode = "ab" if append else "wb"
            out_file = None
            try:
                if out_path == "-":
                    out_file = sys.stdout.buffer if hasattr(sys.stdout, "buffer") else sys.stdout
                else:
                    # Ensure parent dir exists
                    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
                    out_file = open(out_path, mode)
            except Exception as e:
                print(f"Failed to open output '{out_path}': {e}", file=sys.stderr)
                return

            total = 0
            try:
                while True:
                    data = conn.recv(CHUNK_SIZE)
                    if not data:
                        # peer closed connection
                        break
                    out_file.write(data)
                    total += len(data)
                    if not quiet:
                        # simple progress print (bytes)
                        print(f"\rReceived {total:,} bytes", end="", flush=True)
            except BrokenPipeError:
                # Happens if stdout closed (when writing to pipe)
                pass
            except Exception as e:
                print(f"\nError while receiving: {e}", file=sys.stderr)
            finally:
                if out_file is not None and out_path != "-":
                    out_file.close()

            if not quiet:
                print(f"\nDone. Total received: {total:,} bytes")
                if out_path != "-":
                    print(f"Saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Raw TCP receiver (netcat-like) that writes bytes to a file.")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host/interface to bind to (default: 0.0.0.0). Use :: for IPv6.")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    parser.add_argument("--output", "-o", required=True,
                        help="Output file path, or '-' for stdout (careful writing binary to terminal).")
    parser.add_argument("--append", action="store_true", help="Append to output file instead of overwriting")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    args = parser.parse_args()

    receive_raw(args.port, args.host, args.output, append=args.append, quiet=args.quiet)


if __name__ == "__main__":
    main()
