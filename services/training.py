import random
import uuid
from datetime import datetime
from data.words import update_card_stats, get_random_words, CARD_QUESTIONS
from services.notifications import schedule_srs_review

training_sessions = {}


def create_training_session(words_count=10, user_words=None, username=None):
    """Создать новую тренировочную сессию"""
    if user_words is None:
        words = get_random_words(words_count)
    else:
        if words_count > len(user_words):
            words_count = len(user_words)
        if words_count == 0:
            words = []
        else:
            words = random.sample(user_words, min(words_count, len(user_words)))

    session_id = str(uuid.uuid4())[:8]

    training_sessions[session_id] = {
        'session_id': session_id,
        'words': words,
        'current_index': 0,
        'answers': [],
        'finished': False,
        'username': username,
        'created_at': datetime.now().isoformat()
    }

    return training_sessions[session_id]


def get_current_question(session_id):
    """Получить текущий вопрос"""
    session = training_sessions.get(session_id)
    if not session or session['finished']:
        return None

    if session['current_index'] >= len(session['words']):
        session['finished'] = True
        return None

    current_word = session['words'][session['current_index']]

    # Используем CARD_QUESTIONS как общий список слов для вариантов ответов
    all_words = CARD_QUESTIONS
    question = generate_question(current_word, all_words)

    question['word_id'] = current_word['id']
    question['question_number'] = session['current_index'] + 1
    question['total_questions'] = len(session['words'])
    question['current_streak'] = current_word.get('srs_streak', 0)

    return question


def generate_question(current_word, all_words):
    """Сгенерировать вопрос с 4 вариантами ответа"""
    correct_translation = current_word['translation']
    other_translations = [
        w['translation'] for w in all_words
        if w['id'] != current_word['id']
    ]
    other_translations = list(set(other_translations))

    while len(other_translations) < 3:
        other_translations.append("???")

    wrong_options = random.sample(other_translations, min(3, len(other_translations)))
    options = wrong_options + [correct_translation]
    random.shuffle(options)

    return {
        "question": current_word['word'],
        "correct_answer": correct_translation,
        "options": options,
        "difficulty": current_word.get('difficulty', 'easy'),
        "word_id": current_word['id']
    }


def submit_answer(session_id, word_id, selected_answer):
    """Проверить ответ и обновить статистику + запланировать SRS"""
    session = training_sessions.get(session_id)
    if not session or session['finished']:
        return {"error": "Сессия не найдена или завершена"}

    current_word = None
    for word in session['words']:
        if word['id'] == word_id:
            current_word = word
            break

    if not current_word:
        return {"error": "Слово не найдено"}

    is_correct = (selected_answer == current_word['translation'])
    current_streak = current_word.get('srs_streak', 0)

    session['answers'].append({
        'word_id': word_id,
        'word': current_word['word'],
        'translation': current_word['translation'],
        'selected': selected_answer,
        'is_correct': is_correct,
        'timestamp': datetime.now().isoformat()
    })

    # Обновляем статистику в words_data.json
    try:
        update_card_stats(word_id, is_correct)
    except Exception as e:
        print(f"Ошибка обновления статистики слова: {e}")

    srs_info = None
    username = session.get('username')

    if username:
        try:
            srs_info = schedule_srs_review(
                username=username,
                word_id=word_id,
                word_text=current_word['word'],
                streak=current_streak,
                is_correct=is_correct
            )
        except Exception as e:
            print(f"Ошибка создания SRS уведомления: {e}")

    session['current_index'] += 1

    is_finished = session['current_index'] >= len(session['words'])

    if is_finished:
        session['finished'] = True
        correct_count = sum(1 for a in session['answers'] if a['is_correct'])
        total_count = len(session['answers'])
        percentage = round((correct_count / total_count) * 100) if total_count > 0 else 0

        return {
            "is_correct": is_correct,
            "correct_answer": current_word['translation'],
            "finished": True,
            "srs_scheduled": srs_info,
            "results": {
                "correct": correct_count,
                "wrong": total_count - correct_count,
                "total": total_count,
                "percentage": percentage
            }
        }

    return {
        "is_correct": is_correct,
        "correct_answer": current_word['translation'],
        "finished": False,
        "srs_scheduled": srs_info,
        "next_review_in": srs_info['days_until_review'] if srs_info else None
    }


def get_session_results(session_id):
    """Получить результаты сессии"""
    session = training_sessions.get(session_id)
    if not session:
        return None

    correct_count = sum(1 for a in session['answers'] if a['is_correct'])
    total_count = len(session['answers'])

    return {
        "correct": correct_count,
        "wrong": total_count - correct_count,
        "total": total_count,
        "percentage": round((correct_count / total_count) * 100) if total_count > 0 else 0,
        "answers": session['answers'],
        "session_id": session_id
    }


def calculate_xp_for_answer(is_correct, word_difficulty):
    """Рассчитать опыт за ответ"""
    if not is_correct:
        return 0

    xp = 10
    if word_difficulty == 'hard':
        xp += 15
    elif word_difficulty == 'medium':
        xp += 10
    elif word_difficulty == 'easy':
        xp += 5
    elif word_difficulty == 'new':
        xp += 8

    return xp


def get_words_by_level(level, user_words):
    """Получить слова для текущего уровня"""

    def get_difficulty(word):
        total = word.get('correct', 0) + word.get('wrong', 0)
        if total == 0:
            return 'new'
        elif word.get('correct', 0) / total >= 0.8:
            return 'easy'
        elif word.get('correct', 0) / total >= 0.5:
            return 'medium'
        else:
            return 'hard'

    if level <= 1:
        filtered = [w for w in user_words if get_difficulty(w) in ['new', 'easy']]
    elif level == 2:
        filtered = [w for w in user_words if get_difficulty(w) in ['new', 'easy', 'medium']]
    else:
        filtered = user_words

    if len(filtered) < 3:
        return user_words[:10]

    return filtered


def get_training_words(count=10):
    return get_random_words(count)


def get_next_question(session_id):
    return get_current_question(session_id)


def get_due_words_for_review(username, user_words, max_words=None):
    """Получить ТОЛЬКО просроченные слова (due_now)"""
    from services.notifications import get_due_notifications

    due_notifications = get_due_notifications(username)

    # Получаем ID слов, которые нужно повторить прямо сейчас
    due_word_ids = {notif['word_id'] for notif in due_notifications if notif.get('word_id')}

    # Фильтруем слова пользователя - только просроченные
    due_words = [w for w in user_words if w['id'] in due_word_ids]

    print(f"[SRS REVIEW] Найдено просроченных слов: {len(due_words)} из {len(user_words)} всего")

    if max_words and len(due_words) > max_words:
        return random.sample(due_words, max_words)

    return due_words