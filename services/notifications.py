import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

NOTIFICATIONS_FILE = os.path.join(os.path.dirname(__file__), '../data/notifications.json')

# Интервалы повторения в днях (алгоритм SuperMemo-2)
SRS_INTERVALS = {
    0: 0,  # Новое слово
    1: 1,  # 1 день
    2: 3,  # 3 дня
    3: 7,  # неделя
    4: 14,  # 2 недели
    5: 30,  # месяц
    6: 60,  # 2 месяца
    7: 90,  # 3 месяца
    8: 180,  # 6 месяцев
    9: 365,  # год
}


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


def calculate_srs_interval(streak: int, is_correct: bool) -> int:
    """Рассчитать интервал до следующего повторения"""
    if not is_correct:
        new_streak = max(0, streak - 1)
        return SRS_INTERVALS.get(new_streak, 0)
    else:
        new_streak = min(9, streak + 1)
        return SRS_INTERVALS.get(new_streak, 0)


def get_next_review_date(streak: int, is_correct: bool) -> datetime:
    """Получить дату следующего повторения"""
    days = calculate_srs_interval(streak, is_correct)
    return datetime.now() + timedelta(days=days)


def schedule_srs_review(username: str, word_id: int, word_text: str,
                        streak: int, is_correct: bool) -> Dict:
    """Запланировать следующее повторение слова по алгоритму SRS"""
    notifications = _load_notifications()
    if username not in notifications:
        notifications[username] = []

    next_review = get_next_review_date(streak, is_correct)
    new_streak = streak + 1 if is_correct else max(0, streak - 1)

    # Удаляем старые уведомления для этого слова
    notifications[username] = [
        n for n in notifications[username]
        if n.get('word_id') != word_id
    ]

    notification = {
        'id': len(notifications[username]) + 1,
        'word_id': word_id,
        'message': f'Повторение слова "{word_text}"',
        'streak': new_streak,
        'remind_at': next_review.isoformat(),
        'read': False,
        'created_at': datetime.now().isoformat(),
        'type': 'srs_review'
    }

    notifications[username].append(notification)
    _save_notifications(notifications)

    return {
        'notification_id': notification['id'],
        'next_review': next_review.isoformat(),
        'days_until_review': calculate_srs_interval(streak, is_correct),
        'new_streak': new_streak
    }


def get_due_notifications(username: str) -> List[Dict]:
    """Получить уведомления, которые нужно показать сейчас"""
    notifications = _load_notifications()
    if username not in notifications:
        return []

    now = datetime.now()
    due_notifications = []

    for notif in notifications[username]:
        if not notif.get('read', False):
            remind_at = notif.get('remind_at', notif.get('scheduled_at', ''))
            if remind_at:
                scheduled_time = datetime.fromisoformat(remind_at)
                if scheduled_time <= now:
                    due_notifications.append(notif)

    return due_notifications


def get_upcoming_reviews(username: str, days_ahead: int = 7) -> Dict:
    """Получить статистику предстоящих повторений"""
    notifications = _load_notifications()
    if username not in notifications:
        return {'total': 0, 'by_day': {}}

    now = datetime.now()
    end_date = now + timedelta(days=days_ahead)
    by_day = {}

    for notif in notifications[username]:
        if not notif.get('read', False):
            remind_at = notif.get('remind_at', notif.get('scheduled_at', ''))
            if remind_at:
                scheduled_time = datetime.fromisoformat(remind_at)
                if now <= scheduled_time <= end_date:
                    day_key = scheduled_time.strftime('%Y-%m-%d')
                    by_day[day_key] = by_day.get(day_key, 0) + 1

    return {
        'total': sum(by_day.values()),
        'by_day': by_day,
        'period_days': days_ahead
    }


def mark_notification_read(username: str, notification_id: int) -> bool:
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


def mark_all_read(username: str) -> int:
    """Отметить все уведомления как прочитанные"""
    notifications = _load_notifications()
    count = 0
    if username in notifications:
        for notif in notifications[username]:
            if not notif.get('read', False):
                notif['read'] = True
                count += 1
        _save_notifications(notifications)
    return count


def get_srs_stats(username: str) -> Dict:
    """Получить статистику SRS для пользователя"""
    notifications = _load_notifications()
    if username not in notifications:
        return {
            'total_scheduled': 0,
            'due_now': 0,
            'due_today': 0,
            'due_this_week': 0,
            'by_streak': {}
        }

    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59)
    week_end = now + timedelta(days=7)

    stats = {
        'total_scheduled': 0,
        'due_now': 0,
        'due_today': 0,
        'due_this_week': 0,
        'by_streak': {}
    }

    for notif in notifications[username]:
        if not notif.get('read', False) and notif.get('type') == 'srs_review':
            stats['total_scheduled'] += 1

            remind_at = notif.get('remind_at', notif.get('scheduled_at', ''))
            if remind_at:
                try:
                    scheduled_time = datetime.fromisoformat(remind_at)
                    streak = notif.get('streak', 0)

                    streak_key = str(min(9, streak))
                    stats['by_streak'][streak_key] = stats['by_streak'].get(streak_key, 0) + 1

                    if scheduled_time <= now:
                        stats['due_now'] += 1
                    if scheduled_time <= today_end:
                        stats['due_today'] += 1
                    if scheduled_time <= week_end:
                        stats['due_this_week'] += 1
                except Exception as e:
                    print(f"[SRS STATS] Ошибка парсинга даты: {remind_at}, ошибка: {e}")

    print(f"[SRS STATS] Пользователь: {username}, due_now: {stats['due_now']}, due_today: {stats['due_today']}, due_week: {stats['due_this_week']}, total: {stats['total_scheduled']}")
    return stats


def cleanup_old_notifications(username: str, days_old: int = 30) -> int:
    """Удалить старые прочитанные уведомления"""
    notifications = _load_notifications()
    if username not in notifications:
        return 0

    cutoff_date = datetime.now() - timedelta(days=days_old)
    original_count = len(notifications[username])

    notifications[username] = [
        notif for notif in notifications[username]
        if not notif.get('read', False) or
           datetime.fromisoformat(notif['created_at']) > cutoff_date
    ]

    _save_notifications(notifications)
    return original_count - len(notifications[username])