import os
import sys
import urllib.request

# قائمة الدول التي تريد حظرها (ISO 2-letter country codes)
blocked_countries = [
    # دول أوروبا (EU + أوروبا عموماً)
    "AL", "AD", "AT", "BY", "BE", "BA", "BG", "HR", "CY", "CZ",
    "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS", "IE", "IT",
    "LV", "LI", "LT", "LU", "MT", "MD", "MC", "ME", "NL", "MK",
    "NO", "PL", "PT", "RO", "RU", "SM", "RS", "SK", "SI", "ES",
    "SE", "CH", "TR", "UA", "GB", "VA",

    # بالإضافة إلى إيران والهند وأمريكا
    "IR", "IN", "US"
]

IPDENY_BASE_URL = "http://www.ipdeny.com/ipblocks/data/countries/"

def download_country_ip(country_code):
    url = f"{IPDENY_BASE_URL}{country_code.lower()}.zone"
    print(f"تحميل IPs للدولة: {country_code} من {url}")
    try:
        response = urllib.request.urlopen(url)
        data = response.read().decode()
        return data.splitlines()
    except Exception as e:
        print(f"خطأ في تحميل IPs للدولة {country_code}: {e}")
        return []

def generate_iptables_rules(ip_list):
    rules = []
    for ip_range in ip_list:
        rules.append(f"iptables -A INPUT -s {ip_range} -j DROP")
    return rules

def main():
    all_rules = []
    for country in blocked_countries:
        ips = download_country_ip(country)
        rules = generate_iptables_rules(ips)
        all_rules.extend(rules)

    # طباعة القواعد للمراجعة
    print("\n# قواعد iptables للحظر:\n")
    for rule in all_rules:
        print(rule)

    # تأكيد التنفيذ
    confirm = input("\nهل تريد تنفيذ هذه القواعد الآن؟ (yes/no): ").strip().lower()
    if confirm == "yes":
        for rule in all_rules:
            os.system(rule)
        print("\nتم تنفيذ قواعد الحظر بنجاح!")
    else:
        print("تم إلغاء التنفيذ.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("يرجى تشغيل السكربت كـ root (sudo).")
        sys.exit(1)
    main()
