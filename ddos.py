import subprocess
import time
from collections import defaultdict


THRESHOLD = 20  
TIME_FRAME = 40  
BANNED_IPS = set()

def get_incoming_ips():
    """Retrieve incoming IP addresses connected to the server."""
    result = subprocess.run(['netstat', '-ntu'], stdout=subprocess.PIPE)
    lines = result.stdout.decode().split('\n')
    ips = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 5:
            ip = parts[4].split(':')[0]
            if ip and ip != '127.0.0.1':
                ips.append(ip)
    return ips

def ban_ip(ip):
    
    if ip not in BANNED_IPS:
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        BANNED_IPS.add(ip)
        print(f"Banned IP: {ip}")

def monitor():
    
    while True:
        ip_counter = defaultdict(int)
        ips = get_incoming_ips()
        for ip in ips:
            ip_counter[ip] += 1
        
        for ip, count in ip_counter.items():
            if count > THRESHOLD:
                ban_ip(ip)
        
        print("[INFO] Checked connections.")
        time.sleep(TIME_FRAME)

if __name__ == "__main__":
    print("[START] Starting DDoS protection monitoring...")
    monitor()
