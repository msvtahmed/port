from scapy.all import sniff
from collections import defaultdict
import os
import time
import requests

# Define the maximum number of requests per second
THRESHOLD = 20
WEBHOOK_URL = "https://discord.com/api/webhooks/1351189330064048128/Mdv4DesbJFaxg25lFsEpzvxzfUS4qMR-c_MXEZ61xtZhNOo_XMlFTg-me_wgDvDqqhiP"
ip_requests = defaultdict(list)
banned_ips = set()

def send_webhook(ip):
    data = {"content": f"🚨 Suspicious IP blocked: {ip}"}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"[!] Error sending Webhook: {e}")

def block_ip(ip):
    if ip not in banned_ips:
        os.system(f"iptables -A INPUT -s {ip} -j DROP")
        banned_ips.add(ip)
        print(f"[!] {ip} has been permanently blocked due to suspicious activity")
        send_webhook(ip)

def packet_handler(packet):
    if packet.haslayer("IP"):
        src_ip = packet["IP"].src
        current_time = time.time()
        ip_requests[src_ip].append(current_time)
        
        # Remove old requests
        ip_requests[src_ip] = [t for t in ip_requests[src_ip] if current_time - t < 1]
        
        if len(ip_requests[src_ip]) > THRESHOLD:
            block_ip(src_ip)

print("[*] Monitoring network... Press Ctrl+C to stop")
sniff(prn=packet_handler, store=False)
