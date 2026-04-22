import json
import os
import hashlib
import uuid
from datetime import datetime

USERS_FILE = os.path.join(os.path.dirname(__file__), '../data/users_data.json')
QUIZ_LEVELS = [0, 100, 175, 250, 350]


def _load_users():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}


def _save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    users = _load_users()
    if username in users: return False, "Пользователь существует"
    if len(username) < 3: return False, "Мин. 3 символа"
    if len(password) < 4: return False, "Мин. 4 символа"

    users[username] = {
        "username": username,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "words": [],

        # --- ОБЩИЙ УРОВЕНЬ ПОЛЬЗОВАТЕЛЯ (Опыт за знания) ---
        "user_level": {"current": 1, "xp": 0, "next_level_xp": 100},

        # --- АККАУНТ (Баллы за игры) ---
        "account_points": 0,
        "account_level": 1,

        # --- ГЛОБАЛЬНАЯ СТАТИСТИКА ---
        "global_stats": {
            "quiz_played": 0,
            "sprint_played": 0,
            "total_correct": 0,
            "total_wrong": 0
        },

        "sprint_record": 0,
        "games_progress": {
            "cards": {"level": 1, "xp": 0, "next_level_xp": 150},
            "quiz": {"level": 1, "xp": 0, "next_level_xp": 100},
            "sprint": {"level": 1, "xp": 0, "next_level_xp": 150}
        }
    }
    _save_users(users)
    return True, "Успешно"


def login_user(username, password):
    users = _load_users()
    if username not in users: return False, "Не найден", None
    if users[username]["password"] != hash_password(password): return False, "Неверный пароль", None
    return True, str(uuid.uuid4()), username


def get_user_data(username):
    return _load_users().get(username)


def update_user_words(username, words):
    users = _load_users()
    if username in users:
        users[username]["words"] = words
        _save_users(users)
        return True
    return False


def get_user_level(username):
    users = _load_users()
    if username in users:
        return users[username].get("user_level", {"current": 1, "xp": 0})
    return {"current": 1, "xp": 0}


def get_game_progress(username, game_name):
    users = _load_users()
    if username in users:
        games = users[username].get("games_progress", {})
        return games.get(game_name, {"level": 1, "xp": 0})
    return {"level": 1, "xp": 0}


def update_game_progress(username, game_name, xp_gained):
    users = _load_users()
    if username not in users: return False, None, None
    games = users[username].get("games_progress", {})
    game = games.get(game_name, {"level": 1, "xp": 0})
    game["xp"] += xp_gained
    game_level_up = False
    if game_name == 'quiz':
        current_lvl = game["level"]
        if current_lvl < 5 and game["xp"] >= QUIZ_LEVELS[current_lvl]:
            game["level"] += 1
            game_level_up = True
    else:
        if game["xp"] >= game.get("next_level_xp", 150):
            game["xp"] -= game.get("next_level_xp", 150)
            game["level"] += 1
            game["next_level_xp"] = int(game.get("next_level_xp", 150) * 1.3)
            game_level_up = True
    games[game_name] = game
    users[username]["games_progress"] = games
    _save_users(users)
    return game_level_up, game


def update_sprint_record(username, correct_count):
    users = _load_users()
    if username in users:
        current_record = users[username].get("sprint_record", 0)
        if correct_count > current_record:
            users[username]["sprint_record"] = correct_count
            _save_users(users)
            return True
    return False


def add_account_points(username, points):
    """Добавить баллы на аккаунт и пересчитать уровень"""
    users = _load_users()
    if username in users:
        users[username]["account_points"] = users[username].get("account_points", 0) + points
        # Расчет уровня: каждые 150 очков = 1 уровень
        total_points = users[username]["account_points"]
        new_level = 1 + (total_points // 150)
        users[username]["account_level"] = new_level
        _save_users(users)
        return True
    return False


def update_global_stats(username, game_type, correct, wrong):
    """Обновить статистику игр"""
    users = _load_users()
    if username in users:
        stats = users[username].get("global_stats",
                                    {"quiz_played": 0, "sprint_played": 0, "total_correct": 0, "total_wrong": 0})

        if game_type == 'quiz':
            stats["quiz_played"] += 1
        elif game_type == 'sprint':
            stats["sprint_played"] += 1

        stats["total_correct"] += correct
        stats["total_wrong"] += wrong

        users[username]["global_stats"] = stats
        _save_users(users)
        return True
    return False


def get_user_stats(username):
    """Получить статистику и данные аккаунта"""
    users = _load_users()
    if username in users:
        stats = users[username].get("global_stats",
                                    {"quiz_played": 0, "sprint_played": 0, "total_correct": 0, "total_wrong": 0})
        total = stats["total_correct"] + stats["total_wrong"]
        success_rate = round((stats["total_correct"] / total * 100), 1) if total > 0 else 0

        return {
            "account_points": users[username].get("account_points", 0),
            "account_level": users[username].get("account_level", 1),
            "sprint_record": users[username].get("sprint_record", 0),
            "quiz_played": stats["quiz_played"],
            "sprint_played": stats["sprint_played"],
            "total_correct": stats["total_correct"],
            "total_wrong": stats["total_wrong"],
            "success_rate": success_rate
        }
    return {"account_points": 0, "account_level": 1, "sprint_record": 0}