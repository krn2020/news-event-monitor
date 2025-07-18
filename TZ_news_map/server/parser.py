import requests
from datetime import datetime, timedelta

def fetch_events_from_map(date=None):
    if date is None:
        date_obj = datetime.now()
    else:
        date_obj = datetime.strptime(date, "%d.%m.%Y")

    date_str = date_obj.strftime('%d.%m.%Y')
    url = f"https://cdndc.img.ria.ru/dc/kay-n/2022/SOP-content/data/points/data-{date_str}.json"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"❌ Не удалось получить JSON. Статус: {response.status_code}")

    try:
        data = response.json()
    except Exception as e:
        print("Ошибка при парсинге JSON:", response.text[:200])
        raise

    if not isinstance(data, list):
        raise Exception("❌ Ожидался список объектов")

    events = []

    for item in data:
        title = (item.get("icon") or "Событие").strip()
        description = (item.get("text") or "").strip()
        category = (item.get("type") or "").strip()
        # Используем дату, переданную в функцию, чтобы привязать событие к выбранной дате
        event_date_str = date_str
        link = (item.get("link") or "").strip()
        area = (item.get("area") or "").strip()
        name = (item.get("name") or "").strip()
        full_name = (item.get("fullName") or "").strip()

        location = f"{full_name or name} ({area})" if area else full_name or name

        events.append({
            'title': title,
            'description': f"{description} [{location}]" if description else location,
            'category': category,
            'date': event_date_str,
            'link': link
        })
    print("[parser] Событий загружено:", len(events))
    return events
