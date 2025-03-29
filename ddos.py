import subprocess
import time
import requests
from collections import defaultdict, deque

THRESHOLD = 30  
TIME_FRAME = 20  
BANNED_IPS = set()
EXEMPTED_IPS = {"88.214.58.38"}  
WEBHOOK_URL = "https://discord.com/api/webhooks/1351189330064048128/Mdv4DesbJFaxg25lFsEpzvxzfUS4qMR-c_MXEZ61xtZhNOo_XMlFTg-me_wgDvDqqhiP" 

# تتبع IPs عبر عدة دورات
ip_activity = defaultdict(lambda: deque(maxlen=3))

def get_incoming_ips():
    """استرجاع عناوين IP المتصلة بالخادم."""
    try:
        result = subprocess.run(['ss', '-ntu'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = result.stdout.decode().split('\n')
        ips = []
        for line in lines[1:]:  # تجاهل العنوان
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[4].split(':')[0]
                if ip and ip != '127.0.0.1':
                    ips.append(ip)
        return ips
    except Exception as e:
        print(f"[ERROR] Failed to get incoming IPs: {e}")
        return []

def send_webhook_notification(ip):
    """إرسال إشعار عند حظر IP."""
    data = {"content": f"🚨 تم حظر الـ IP المشبوه: `{ip}` 🚫"}
    for _ in range(3):  # إعادة المحاولة 3 مرات
        try:
            response = requests.post(WEBHOOK_URL, json=data, timeout=5)
            if response.status_code == 204:
                print(f"[WEBHOOK] Notification sent for IP: {ip}")
                return
            else:
                print(f"[WEBHOOK] Failed to send notification for IP: {ip}, Status: {response.status_code}")
        except Exception as e:
            print(f"[WEBHOOK] Error sending notification: {e}")
        time.sleep(2)  # الانتظار قبل إعادة المحاولة

def ban_ip(ip):
    """حظر IP مشبوه باستخدام iptables."""
    if ip not in BANNED_IPS and ip not in EXEMPTED_IPS:
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        BANNED_IPS.add(ip)
        print(f"[SECURITY] 🚫 Banned IP: {ip}")
        send_webhook_notification(ip)

def monitor():
    """مراقبة نشاط الشبكة للكشف عن أي هجوم DDoS."""
    while True:
        ip_counter = defaultdict(int)
        ips = get_incoming_ips()

        for ip in ips:
            ip_counter[ip] += 1
            ip_activity[ip].append(time.time())  # سجل الوقت

        for ip, count in ip_counter.items():
            if len(ip_activity[ip]) >= 3:  # التحقق من النشاط المتكرر
                time_diff = ip_activity[ip][-1] - ip_activity[ip][0]
                if time_diff < TIME_FRAME and count > THRESHOLD:
                    ban_ip(ip)

        print("[INFO]  Checked connections.")
        time.sleep(TIME_FRAME)

if __name__ == "__main__":
    print("[START] 🚀 Starting DDoS protection monitoring...")
    monitor()
