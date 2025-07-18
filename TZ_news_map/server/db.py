import psycopg2
from datetime import datetime, timedelta

DB_NAME = "postgres1"
DB_USER = "postgres"
DB_PASS = "12345"
DB_HOST = "localhost"

def save_events(events):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        category TEXT,
        date DATE,
        link TEXT
    )
    """)

    for e in events:
        # Проверка, есть ли уже такое событие
        cur.execute("""
            SELECT 1 FROM events 
            WHERE title = %s AND description = %s AND category = %s AND date = %s
        """, (
            e['title'],
            e['description'],
            e['category'],
            datetime.strptime(e['date'], "%d.%m.%Y").date()
        ))
        exists = cur.fetchone()
        if exists:
            continue  # Пропускаем уже существующее событие

        # Вставка, если не существует
        cur.execute("""
            INSERT INTO events (title, description, category, date, link)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            e['title'],
            e['description'],
            e['category'],
            datetime.strptime(e['date'], "%d.%m.%Y").date(),
            e['link']
        ))

    conn.commit()
    cur.close()
    conn.close()

def get_events_by_date(date_str):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    # Преобразуем строку даты в объект date
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()

    cur.execute("SELECT title, category, description, date, link FROM events WHERE date = %s", (date_obj,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{'title': r[0], 'category': r[1], 'description': r[2], 'date': r[3].strftime("%d.%m.%Y"), 'link': r[4] or ""} for r in rows]

