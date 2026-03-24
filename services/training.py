import random
import uuid
from data.words import get_all_words, get_word_by_id, update_card_stats, get_random_words

training_sessions = {}


def create_training_session(words_count=10):
    """Создать новую тренировочную сессию"""
    words = get_random_words(words_count)

    session_id = str(uuid.uuid4())[:8]

    training_sessions[session_id] = {
        'session_id': session_id,
        'words': words,
        'current_index': 0,
        'answers': [],
        'finished': False
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

    all_words = get_all_words()
    question = generate_question(current_word, all_words)
    question['word_id'] = current_word['id']
    question['question_number'] = session['current_index'] + 1
    question['total_questions'] = len(session['words'])

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

    wrong_options = random.sample(other_translations, 3)

    # Собираем все варианты
    options = wrong_options + [correct_translation]
    random.shuffle(options)

    return {
        "question": current_word['word'],
        "correct_answer": correct_translation,
        "options": options
    }


def submit_answer(session_id, word_id, selected_answer):
    """Проверить ответ и обновить статистику"""
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

    session['answers'].append({
        'word_id': word_id,
        'word': current_word['word'],
        'translation': current_word['translation'],
        'selected': selected_answer,
        'is_correct': is_correct
    })

    update_card_stats(word_id, is_correct)

    session['current_index'] += 1

    is_finished = session['current_index'] >= len(session['words'])

    if is_finished:
        session['finished'] = True
        # Рассчитываем результат
        correct_count = sum(1 for a in session['answers'] if a['is_correct'])
        total_count = len(session['answers'])
        percentage = round((correct_count / total_count) * 100) if total_count > 0 else 0

        return {
            "is_correct": is_correct,
            "correct_answer": current_word['translation'],
            "finished": True,
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
        "finished": False
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
        "answers": session['answers']
    }


def check_answer(session_id, word_id, selected_answer):
    """Алиас для submit_answer (для обратной совместимости)"""
    return submit_answer(session_id, word_id, selected_answer)


def get_training_words(count=10):
    """Получить слова для тренировки"""
    return get_random_words(count)


def get_next_question(session_id):
    """Получить следующий вопрос (алиас)"""
    return get_current_question(session_id)