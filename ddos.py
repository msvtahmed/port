from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def home():
    # تأخير 5 ثواني لحماية DDoS
    time.sleep(5)
    return "مرحبًا بك في السيرفر بعد الانتظار."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

