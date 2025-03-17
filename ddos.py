import subprocess
import time
import requests
from collections import defaultdict

THRESHOLD = 20  
TIME_FRAME = 40  
BANNED_IPS = set()
EXEMPTED_IPS = {"88.214.58.38"}  
WEBHOOK_URL = "https://discord.com/api/webhooks/1351189330064048128/Mdv4DesbJFaxg25lFsEpzvxzfUS4qMR-c_MXEZ61xtZhNOo_XMlFTg-me_wgDvDqqhiP" 

def get_incoming_ips():
    """استرجاع عناوين IP المتصلة بالخادم."""
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

def send_webhook_notification(ip):
    """هون ببين يلي راح ينحظرو."""
    data = {
        "content": f"الاخ ددوس خذ باند: `{ip}` !"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"[WEBHOOK] Notification sent for IP: {ip}")
        else:
            print(f"[WEBHOOK] Failed to send notification for IP: {ip}")
    except Exception as e:
        print(f"[WEBHOOK] Error sending notification: {e}")

def ban_ip(ip):
    """هون بتراقب ال ip"""
    if ip not in BANNED_IPS and ip not in EXEMPTED_IPS:
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        BANNED_IPS.add(ip)
        print(f"Banned IP: {ip}")
        send_webhook_notification(ip)

def monitor():
    """هون بنقلعو وبوخذو حظر."""
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
