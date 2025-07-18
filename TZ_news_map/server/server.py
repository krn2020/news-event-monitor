import socket
import threading
import json
from parser import fetch_events_from_map
from db import save_events, get_events_by_date
from collections import Counter

HOST = '0.0.0.0'
PORT = 9009

def log_grouped_statistics(events):
    counter = Counter(e['title'] for e in events)
    print("\n[статистика] События по категориям:")
    for title, count in counter.most_common():
        print(f"🔹 {title}: {count}")

def handle_client(conn, addr):
    print(f"[+] Client connected: {addr}")
    data = conn.recv(1024).decode().strip()
    print(f"[>] Получено от клиента: {data}")

    try:
        # Ожидаем, что клиент отправляет дату в формате "dd.mm.yyyy"
        date_str = data
        # Загружаем и сохраняем события для указанной даты
        events = fetch_events_from_map(date_str)
        log_grouped_statistics(events)
        save_events(events)
        # Берём события из базы по дате
        events_for_date = get_events_by_date(date_str)
        # Отправляем клиенту
        conn.sendall(json.dumps(events_for_date, ensure_ascii=False).encode())
        print(f"[✓] Отправлено событий за {date_str}: {len(events_for_date)}")
    except Exception as e:
        error_msg = f"Ошибка обработки запроса: {e}"
        print(error_msg)
        conn.sendall(error_msg.encode())

    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    start_server()
