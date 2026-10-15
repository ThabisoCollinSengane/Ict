"""Serve trades_chart.html over HTTP so you can open it on your phone.

Usage (run on VPS):
    python scripts/serve.py

Then open on your phone:
    http://<VPS_PUBLIC_IP>:8080/trades_chart.html

IMPORTANT — AWS security group: you must allow inbound TCP port 8080
from your IP (or 0.0.0.0/0) in the EC2 security group first.
Go to: AWS Console → EC2 → Security Groups → Inbound rules → Add rule
Type: Custom TCP | Port: 8080 | Source: My IP (or Anywhere)

Stop with Ctrl+C.
"""

import http.server
import os
import socket
import socketserver

PORT = 8080
DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "histdata"))


def _public_ip() -> str:
    try:
        import urllib.request
        return urllib.request.urlopen("https://api.ipify.org", timeout=4).read().decode()
    except Exception:
        return "<your-vps-ip>"


def main():
    if not os.path.exists(DIR):
        print(f"ERROR: data directory not found: {DIR}")
        return

    ip = _public_ip()
    print(f"\n{'='*55}")
    print(f"  Serving: {DIR}")
    print(f"  Local:   http://localhost:{PORT}/trades_chart.html")
    print(f"  Phone:   http://{ip}:{PORT}/trades_chart.html")
    print(f"{'='*55}")
    print("  Requires port 8080 open in AWS security group.")
    print("  Stop with Ctrl+C\n")

    os.chdir(DIR)
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
