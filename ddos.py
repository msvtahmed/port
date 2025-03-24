import scapy.all as scapy
from collections import defaultdict
import os
import time

# إعداد معايير الاشتباه
REQUEST_THRESHOLD = 30  # الحد الأقصى للطلبات في الثانية قبل حظر IP
BAN_TIME = 300  # مدة الحظر بالثواني (5 دقائق)
MONITORED_INTERFACE = "eth0"  # الواجهة التي سيتم مراقبتها (عدلها حسب شبكتك)

# قائمة لتتبع عدد الطلبات لكل IP
ip_request_count = defaultdict(int)
banned_ips = {}

def block_ip(ip):
    """إضافة IP إلى قائمة الحظر باستخدام iptables"""
    if ip not in banned_ips:
        print(f"[!] حظر IP مشبوه: {ip}")
        os.system(f"iptables -A INPUT -s {ip} -j DROP")
        banned_ips[ip] = time.time()  # تسجيل وقت الحظر

def unblock_expired_ips():
    """إزالة الحظر بعد BAN_TIME"""
    current_time = time.time()
    for ip in list(banned_ips.keys()):
        if current_time - banned_ips[ip] > BAN_TIME:
            print(f"[+] إزالة الحظر عن: {ip}")
            os.system(f"iptables -D INPUT -s {ip} -j DROP")
            del banned_ips[ip]

def process_packet(packet):
    """تحليل الحزم الواردة"""
    if packet.haslayer(scapy.IP):  
        ip_src = packet[scapy.IP].src
        ip_request_count[ip_src] += 1

        if ip_request_count[ip_src] > REQUEST_THRESHOLD:
            block_ip(ip_src)

def monitor_traffic():
    """مراقبة الترافيك الحي"""
    print("[*] بدء مراقبة الترافيك... اضغط Ctrl+C للإيقاف.")
    try:
        while True:
            scapy.sniff(iface=MONITORED_INTERFACE, prn=process_packet, store=False, count=10)
            unblock_expired_ips()  # إزالة الحظر عن IPs القديمة
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] إيقاف المراقبة. تنظيف الحظر...")
        for ip in banned_ips.keys():
            os.system(f"iptables -D INPUT -s {ip} -j DROP")

if __name__ == "__main__":
    monitor_traffic()
