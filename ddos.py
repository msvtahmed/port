import os
import requests

# مصادر قوائم الحظر (يمكنك إضافة المزيد)
BLACKLIST_URLS = [
    "https://iplists.firehol.org/files/firehol_level1.netset",  # FireHOL Level 1
    "https://www.spamhaus.org/drop/drop.txt"  # Spamhaus DROP List
]

BLACKLIST_FILE = "/tmp/blacklist_ips.txt"

def download_blacklist():
    """تحميل قائمة عناوين IP المشبوهة وحفظها في ملف"""
    print("[*] تحميل قائمة الحظر...")
    with open(BLACKLIST_FILE, "w") as file:
        for url in BLACKLIST_URLS:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    file.write(response.text + "\n")
                    print(f"[+] تم تحميل القائمة من: {url}")
                else:
                    print(f"[!] فشل تحميل القائمة من: {url}")
            except requests.RequestException as e:
                print(f"[!] خطأ أثناء التحميل: {e}")

def block_ips():
    """حظر عناوين IP المشبوهة باستخدام iptables"""
    print("[*] بدء عملية الحظر...")
    with open(BLACKLIST_FILE, "r") as file:
        for line in file:
            ip = line.strip()
            if ip and not ip.startswith("#"):
                os.system(f"iptables -A INPUT -s {ip} -j DROP")
                print(f"[BLOCKED] حظر IP: {ip}")

def main():
    download_blacklist()
    block_ips()
    print("[✅] تم تفعيل الحماية ضد الهجمات!")

if __name__ == "__main__":
    main()
