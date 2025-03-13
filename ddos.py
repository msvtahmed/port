import time
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Protection settings
REQUEST_LIMIT = 100        # Maximum allowed requests
TIME_WINDOW = 30           # Time window in seconds
BLOCK_DURATION = 3600      # IP block duration in seconds (1 hour)

# Simple request log database
request_log = {}
blocked_ips = {}

# Function to block an IP using iptables
def block_ip(ip):
    if ip not in blocked_ips:
        print(f"[BLOCK] Blocking IP: {ip}")
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
        blocked_ips[ip] = time.time()

# Function to unblock IPs after block duration expires
def unblock_ips():
    current_time = time.time()
    for ip in list(blocked_ips):
        if current_time - blocked_ips[ip] > BLOCK_DURATION:
            print(f"[UNBLOCK] Unblocking IP: {ip}")
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
            del blocked_ips[ip]

@app.route("/")
def index():
    client_ip = request.remote_addr
    current_time = time.time()

    # Update request log
    if client_ip not in request_log:
        request_log[client_ip] = []

    # Remove old requests from the log
    request_log[client_ip] = [t for t in request_log[client_ip] if current_time - t < TIME_WINDOW]
    request_log[client_ip].append(current_time)

    # Check if the request limit is exceeded
    if len(request_log[client_ip]) > REQUEST_LIMIT:
        block_ip(client_ip)
        return jsonify({"error": "You have been blocked due to too many requests."}), 403

    # Unblock expired IPs
    unblock_ips()

    return jsonify({"message": "Welcome! Your request is safe."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
