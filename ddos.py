import socket
import struct
import time
import requests
from collections import Counter

# إعداد متغيرات المراقبة
HOST = "0.0.0.0"  # الاستماع على جميع الواجهات
INTERVAL = 10  # مدة التحليل بالثواني
WEBHOOK_URL = "https://discord.com/api/webhooks/1351189330064048128/Mdv4DesbJFaxg25lFsEpzvxzfUS4qMR-c_MXEZ61xtZhNOo_XMlFTg-me_wgDvDqqhiP"  # رابط الويب هوك

# إنشاء قاموس لتتبع عدد الاتصالات لكل منفذ
port_counts = Counter()

# قائمة المنفذين المستبعدين
excluded_ports = [2022, 3306]

def send_webhook_alert(port, count):
    data = {
        "content": f"🚨 تنبيه: المنفذ {port} يتلقى هجومًا محتملاً بعدد طلبات: {count}"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"[!] فشل إرسال التنبيه إلى Webhook: {e}")

def analyze_traffic():
    global port_counts

    # إنشاء سوكيت للاستماع على جميع الحزم
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.bind((HOST, 0))

    while True:
        start_time = time.time()
        port_counts.clear()

        while time.time() - start_time < INTERVAL:
            packet, addr = sock.recvfrom(65535)
            ip_header = packet[:20]
            ip_data = struct.unpack('!BBHHHBBH4s4s', ip_header)
            protocol = ip_data[6]

            if protocol == 6:  # 6 = بروتوكول TCP
                tcp_header = packet[20:40]
                tcp_data = struct.unpack('!HHLLBBHHH', tcp_header)
                dest_port = tcp_data[1]

                # تجاهل المنافذ المستبعدة
                if dest_port in excluded_ports:
                    continue

                port_counts[dest_port] += 1

        # العثور على المنفذ الأكثر استقبالاً للطلبات
        if port_counts:
            most_attacked_port = port_counts.most_common(1)[0]
            print(f"[!] أكثر منفذ مستهدف: {most_attacked_port[0]} بعدد طلبات: {most_attacked_port[1]}")
            send_webhook_alert(most_attacked_port[0], most_attacked_port[1])
        else:
            print("[*] لم يتم رصد نشاط غير طبيعي.")

if __name__ == "__main__":
    print("[*] بدء مراقبة الهجمات على المنافذ...")
    analyze_traffic()
