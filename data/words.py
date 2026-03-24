import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), 'words_data.json')

DEFAULT_WORDS = [
    {"id": 1, "word": "Привет", "translation": "Hello", "correct": 0, "wrong": 0},
    {"id": 2, "word": "Спасибо", "translation": "Thank you", "correct": 0, "wrong": 0},
    {"id": 3, "word": "Пожалуйста", "translation": "Please", "correct": 0, "wrong": 0},
    {"id": 4, "word": "Извините", "translation": "Sorry", "correct": 0, "wrong": 0},
    {"id": 5, "word": "Доброе утро", "translation": "Good morning", "correct": 0, "wrong": 0},
    {"id": 6, "word": "Спокойной ночи", "translation": "Good night", "correct": 0, "wrong": 0},
    {"id": 7, "word": "Как дела?", "translation": "How are you?", "correct": 0, "wrong": 0},
    {"id": 8, "word": "Отлично", "translation": "Great", "correct": 0, "wrong": 0},
    {"id": 9, "word": "Друг", "translation": "Friend", "correct": 0, "wrong": 0},
    {"id": 10, "word": "Семья", "translation": "Family", "correct": 0, "wrong": 0},
    {"id": 11, "word": "Работа", "translation": "Work", "correct": 0, "wrong": 0},
    {"id": 12, "word": "Учеба", "translation": "Study", "correct": 0, "wrong": 0},
]


def _load_words():
    """Загрузить слова из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        _save_words(DEFAULT_WORDS)
        return DEFAULT_WORDS.copy()


def _save_words(words):
    """Сохранить слова в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def get_all_words():
    """Получить все слова"""
    return _load_words()


def get_word_by_id(word_id):
    """Получить слово по ID"""
    words = _load_words()
    for word in words:
        if word['id'] == word_id:
            return word
    return None


def update_card_stats(word_id, is_correct):
    """Обновить статистику карточки"""
    words = _load_words()

    for word in words:
        if word['id'] == word_id:
            if is_correct:
                word['correct'] += 1
            else:
                word['wrong'] += 1

            _save_words(words)
            return True

    return False


def get_random_words(count=10):
    """Получить случайные слова (без повторений)"""
    words = _load_words()

    if count > len(words):
        count = len(words)

    shuffled = random.sample(words, len(words))
    return shuffled[:count]


def get_cards():
    """Получить все карточки (для API)"""
    from flask import jsonify
    words = _load_words()
    return jsonify(words)