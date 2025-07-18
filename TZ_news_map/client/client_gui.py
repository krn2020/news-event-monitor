import sys
import socket
import json
import webbrowser
from collections import Counter
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTextBrowser, QMessageBox, QFileDialog, QLabel, QDateEdit
)
from PySide6.QtCore import Qt, QDate

HOST = "localhost"
PORT = 9009


def recv_all(sock):
    data = b""
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data.decode("utf-8")


def highlight_words(text, words):
    for word in words:
        if not word:
            continue
        text = text.replace(
            word,
            f"<span style='background-color: yellow'>{word}</span>"
        )
    return text


class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📺 Новости СВО — Клиент")
        self.setMinimumSize(800, 600)

        self.all_events = []

        layout = QVBoxLayout(self)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd.MM.yyyy")
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setToolTip("Текущая дата")
        layout.addWidget(QLabel("Текущая дата:"))
        layout.addWidget(self.date_picker)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск (например: белгород атака)")
        self.search_input.textChanged.connect(self.filter_events)
        layout.addWidget(self.search_input)

        self.btn_fetch = QPushButton("🔄 Загрузить события")
        self.btn_fetch.clicked.connect(self.fetch_events)
        layout.addWidget(self.btn_fetch)

        self.btn_title_stats = QPushButton("📊 Статистика по заголовкам")
        self.btn_title_stats.clicked.connect(self.show_title_statistics)
        layout.addWidget(self.btn_title_stats)

        self.result_label = QLabel("Всего событий: 0")
        layout.addWidget(self.result_label)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)

    def show_title_statistics(self):
        if not self.all_events:
            QMessageBox.information(self, "Статистика", "Нет загруженных событий.")
            return

        title_counter = Counter()

        for event in self.all_events:
            title = event.get("title", "").strip()
            if title:
                title_counter[title] += 1

        if not title_counter:
            QMessageBox.information(self, "Статистика", "Нет заголовков для анализа.")
            return

        top_titles = title_counter.most_common(20)  # Топ-20 заголовков
        stats_text = "\n".join([f"🔹 {title} — {count} раз(а)" for title, count in top_titles])

        QMessageBox.information(self, "Статистика по заголовкам", stats_text)

    def fetch_events(self):
        try:
            date_str = self.date_picker.date().toString("dd.MM.yyyy")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(date_str.encode("utf-8"))
                raw_data = recv_all(s)

                if not raw_data.strip():
                    raise Exception("Сервер вернул пустой ответ")

                self.all_events = json.loads(raw_data)
                self.result_label.setText(f"Всего событий: {len(self.all_events)}")
                self.filter_events()

        except Exception as ex:
            QMessageBox.critical(self, "Ошибка", str(ex))

    def filter_events(self):
        query = self.search_input.text().lower()
        words = query.split()
        self.browser.clear()

        html_output = ""
        match_count = 0

        for e in self.all_events:
            combined_text = f"{e['title']} {e['description']} {e['category']} {e['date']}".lower()
            if all(word in combined_text for word in words):
                match_count += 1
                title = highlight_words(e['title'], words)
                description = highlight_words(e['description'], words)
                date = e['date']
                link = e.get('link', '').strip()

                html_output += f"<p><b>🔹 {title}</b> | <i>{date}</i><br>{description}"
                if link:
                    html_output += f"<br><a href='{link}' style='color:blue; text-decoration:underline;'>🔗 Ссылка на новость</a>"
                html_output += "</p><hr>"

        self.result_label.setText(f"Всего событий: {len(self.all_events)} | Найдено: {match_count}")

        if not html_output:
            self.browser.setHtml("<p><i>Ничего не найдено</i></p>")
        else:
            self.browser.setHtml(html_output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec())
