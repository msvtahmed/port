import socket
import threading
from collections import defaultdict

MAX_CONNECTIONS = 15
MAX_CONN_PER_IP = 5

lock = threading.Lock()
current_connections = 0
connections_per_ip = defaultdict(int)

def handle_client(client_socket, addr):
    global current_connections
    ip = addr[0]
    try:
        client_socket.sendall("أهلاً وسهلاً!".encode('utf-8'))
        client_socket.recv(1024)
    except:
        pass
    finally:
        with lock:
            current_connections -= 1
            connections_per_ip[ip] -= 1
        client_socket.close()

def run_server(host='0.0.0.0', port=8971):
    global current_connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"السيرفر شغّال ع {host}:{port} ...")
        while True:
            client_socket, addr = server.accept()
            ip = addr[0]

            with lock:
                if current_connections >= MAX_CONNECTIONS or connections_per_ip[ip] >= MAX_CONN_PER_IP:
                    try:
                        client_socket.sendall("الموقع مليان أو وصلت حد الاتصالات من IP تبعك.\n".encode('utf-8'))
                    except:
                        pass
                    client_socket.close()
                    continue
                current_connections += 1
                connections_per_ip[ip] += 1

            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()
