import subprocess
import time
from collections import defaultdict

# إعدادات الحماية
THRESHOLD = 20  # الحد الأقصى لعدد الاتصالات المسموح بها لكل IP
TIME_FRAME = 40  # الفترة الزمنية للتحقق بالثواني
BANNED_IPS = set()

def get_incoming_ips():
    """الحصول على عناوين IP المتصلة بالخادم."""
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
    """حظر عنوان IP باستخدام iptables."""
    if ip not in BANNED_IPS:
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        BANNED_IPS.add(ip)
        print(f"تم حظر IP: {ip}")

def monitor():
    """مراقبة الاتصالات وحظر IPs المشبوهة."""
    while True:
        ip_counter = defaultdict(int)
        ips = get_incoming_ips()
        for ip in ips:
            ip_counter[ip] += 1
        
        for ip, count in ip_counter.items():
            if count > THRESHOLD:
                ban_ip(ip)
        
        print("[INFO] تم التحقق من الاتصالات.")
        time.sleep(TIME_FRAME)

if __name__ == "__main__":
    print("[START] بدء مراقبة الحماية من DDoS...")
    monitor()
