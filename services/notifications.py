import json
import os
from datetime import datetime, timedelta

NOTIFICATIONS_FILE = os.path.join(os.path.dirname(__file__), '../data/notifications.json')

def _load_notifications():
    """Загрузить уведомления"""
    os.makedirs(os.path.dirname(NOTIFICATIONS_FILE), exist_ok=True)
    if not os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}

    try:
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        return {}

def _save_notifications(notifications):
    """Сохранить уведомления"""
    with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(notifications, f, ensure_ascii=False, indent=2)

def schedule_reminder(username, word_id, message):
    """Запланировать напоминание"""
    notifications = _load_notifications()
    if username not in notifications:
        notifications[username] = []

    remind_time = datetime.now() + timedelta(hours=24)
    notification_id = len(notifications[username]) + 1

    notifications[username].append({
        'id': notification_id,
        'word_id': word_id,
        'message': message,
        'remind_at': remind_time.isoformat(),
        'read': False,
        'created_at': datetime.now().isoformat()
    })

    _save_notifications(notifications)
    return notification_id

def get_user_notifications(username):
    """Получить непрочитанные уведомления пользователя"""
    notifications = _load_notifications()
    if username not in notifications:
        return []

    now = datetime.now()
    active_notifications = []

    for notif in notifications[username]:
        if not notif.get('read', False):
            remind_time = datetime.fromisoformat(notif['remind_at'])
            if remind_time <= now:
                active_notifications.append(notif)

    return active_notifications

def mark_notification_read(username, notification_id):
    """Отметить уведомление как прочитанное"""
    notifications = _load_notifications()
    if username in notifications:
        for notif in notifications[username]:
            if notif['id'] == notification_id:
                notif['read'] = True
                break

        _save_notifications(notifications)
        return True
    return False