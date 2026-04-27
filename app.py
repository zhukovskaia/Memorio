from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from datetime import datetime
from functools import wraps
from services.games import start_game, get_current_question, submit_answer, get_game_results, finish_sprint
from auth.user_manager import (
    register_user, login_user, get_user_data, update_user_words,
    get_user_level, get_game_progress, update_game_progress, add_account_points,
    update_sprint_record, get_user_stats, update_global_stats
)
from services.notifications import (
    get_due_notifications, mark_notification_read, get_srs_stats,
    get_upcoming_reviews, mark_all_read, schedule_srs_review
)

app = Flask(__name__)
app.secret_key = 'python-memorio-secret-key-2024'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, result, username = login_user(username, password)
        if success:
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', message=result, message_type='error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            return render_template('register.html', message='Пароли не совпадают', message_type='error')
        success, message = register_user(username, password)
        if success:
            return render_template('login.html', message='Регистрация успешна!', message_type='success')
        return render_template('register.html', message=message, message_type='error')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))


@app.route('/game/cards')
@login_required
def game_cards():
    return render_template('game.html', game_name="cards", game_title="📇 Карточки")


@app.route('/game/quiz')
@login_required
def game_quiz():
    return render_template('game.html', game_name="quiz", game_title="❓ Викторина")


@app.route('/game/sprint')
@login_required
def game_sprint():
    return render_template('sprint.html')


@app.route('/study')
@login_required
def study():
    return render_template('study.html')


@app.route('/srs-train')
@login_required
def srs_train():
    return render_template('srs_train.html')


@app.route('/api/game/<game_name>/progress')
@login_required
def api_get_game_progress(game_name):
    progress = get_game_progress(session['username'], game_name)
    return jsonify(progress)


@app.route('/api/game/start', methods=['POST'])
@login_required
def api_start_game():
    data = request.json
    game_name = data.get('game_name')
    user_data = get_user_data(session['username'])
    game_progress = get_game_progress(session['username'], game_name)
    level = game_progress.get('level', 1)
    game_id = start_game(game_name, level)
    total_q = 10 if game_name != 'cards' else 15
    return jsonify({"game_id": game_id, "total_questions": total_q})


@app.route('/api/game/question/<game_id>')
@login_required
def api_get_game_question(game_id):
    question = get_current_question(game_id)
    if question:
        return jsonify(question)
    return jsonify({"finished": True}), 200


@app.route('/api/game/answer', methods=['POST'])
@login_required
def api_game_answer():
    data = request.json
    game_id = data.get('game_id')
    game_name = data.get('game_name')
    word_id = data.get('word_id')
    selected_answer = data.get('answer')
    result = submit_answer(game_id, word_id, selected_answer)

    if result.get('finished'):
        xp_earned = result.get('results', {}).get('xp_earned', 0)

        if game_name != 'cards':
            _, game = update_game_progress(session['username'], game_name, xp_earned)
            result['game_progress'] = game

        if game_name == 'quiz':
            add_account_points(session['username'], xp_earned)

        if game_name == 'quiz':
            correct = result.get('results', {}).get('correct', 0)
            wrong = result.get('results', {}).get('wrong', 0)
            update_global_stats(session['username'], 'quiz', correct, wrong)

        create_srs_for_game_words(game_id, session['username'])

    return jsonify(result)


@app.route('/api/game/sprint/start', methods=['POST'])
@login_required
def api_start_sprint():
    data = request.json
    level = data.get('level', 1)
    game_id = start_game('sprint', level)
    return jsonify({"game_id": game_id})


@app.route('/api/game/sprint/answer', methods=['POST'])
@login_required
def api_sprint_answer():
    data = request.json
    result = submit_answer(data['game_id'], data['word_id'], data['answer'])
    return jsonify(result)


@app.route('/api/game/sprint/finish', methods=['POST'])
@login_required
def api_finish_sprint():
    data = request.json
    game_id = data['game_id']
    result = finish_sprint(game_id)

    if result:
        update_sprint_record(session['username'], result['correct'])
        add_account_points(session['username'], result['sprint_score'])
        update_global_stats(session['username'], 'sprint', result['correct'], result['wrong'])
        result['account_points_earned'] = result['sprint_score']
        create_srs_for_game_words(game_id, session['username'])

    return jsonify(result)


@app.route('/api/game/<game_id>/results')
@login_required
def api_get_game_results(game_id):
    results = get_game_results(game_id)
    if results:
        return jsonify(results)
    return jsonify({"error": "Not found"}), 404


@app.route('/api/user/stats')
@login_required
def api_user_stats():
    return jsonify(get_user_stats(session['username']))


# ===== ФУНКЦИЯ СОЗДАНИЯ SRS ПОСЛЕ ИГР =====

def create_srs_for_game_words(game_id, username):
    """
    Создает SRS уведомления для всех слов из игры.
    Автоматически добавляет новые слова в профиль пользователя.
    """
    from services.games import active_games
    from data.words import QUIZ_QUESTIONS

    game = active_games.get(game_id)
    if not game:
        print(f"[SRS] Игра {game_id} не найдена")
        return

    user_data = get_user_data(username)
    if not user_data:
        print(f"[SRS] Пользователь {username} не найден")
        return

    user_words = user_data.get('words', [])

    user_words_by_text = {}
    for w in user_words:
        word_text = w.get('word', '').strip().lower()
        user_words_by_text[word_text] = w

    quiz_words_by_text = {}
    for q in QUIZ_QUESTIONS:
        word_text = q.get('word', '').strip().lower()
        quiz_words_by_text[word_text] = q

    print(f"[SRS] ========================================")
    print(f"[SRS] Игра: {game_id}, тип: {game['game_type']}")
    print(f"[SRS] Пользователь: {username}")
    print(f"[SRS] Ответов в игре: {len(game.get('answers', []))}")
    print(f"[SRS] Слов у пользователя ДО: {len(user_words)}")

    srs_created = 0
    new_words_added = 0
    max_id = max([w.get('id', 0) for w in user_words], default=0)

    for answer in game.get('answers', []):
        is_correct = answer.get('is_correct')

        if is_correct is None:
            continue

        word_text = answer.get('word', '').strip().lower()
        if not word_text:
            continue

        user_word = user_words_by_text.get(word_text)

        if not user_word:
            quiz_word = quiz_words_by_text.get(word_text)
            max_id += 1
            new_word = {
                "id": max_id,
                "word": answer.get('word', word_text),
                "translation": answer.get('correct_answer', quiz_word.get('translation', '') if quiz_word else ''),
                "difficulty": "easy",
                "correct": 0,
                "wrong": 0,
                "srs_streak": 0,
                "last_reviewed": None,
                "next_review": None
            }
            user_words.append(new_word)
            user_words_by_text[word_text] = new_word
            user_word = new_word
            new_words_added += 1
            print(f"[SRS] + Добавлено новое слово: '{word_text}'")

        current_streak = user_word.get('srs_streak', 0)

        if is_correct:
            user_word['correct'] = user_word.get('correct', 0) + 1
            user_word['srs_streak'] = min(9, current_streak + 1)
        else:
            user_word['wrong'] = user_word.get('wrong', 0) + 1
            user_word['srs_streak'] = max(0, current_streak - 1)

        user_word['last_reviewed'] = datetime.now().isoformat()
        new_streak = user_word['srs_streak']

        srs_info = schedule_srs_review(
            username=username,
            word_id=user_word['id'],
            word_text=user_word.get('word', word_text),
            streak=current_streak,
            is_correct=is_correct
        )

        days = srs_info.get('days_until_review', 0)
        status = "🟢" if is_correct else "🔴"
        print(
            f"[SRS] {status} '{user_word.get('word')}' | streak: {current_streak}->{new_streak} | повтор через: {days} дн.")
        srs_created += 1

    if srs_created > 0 or new_words_added > 0:
        update_user_words(username, user_words)
        print(f"[SRS] ========================================")
        print(f"[SRS] ✅ ИТОГ: SRS создано: {srs_created}, новых слов: {new_words_added}, всего слов: {len(user_words)}")
    else:
        print(f"[SRS] ❌ Ничего не обновлено")


# ===== TRAINING ENDPOINTS =====

@app.route('/api/training/start', methods=['POST'])
@login_required
def api_start_training():
    from services.training import create_training_session

    data = request.json
    words_count = data.get('count', 10)

    user_data = get_user_data(session['username'])
    user_words = user_data.get('words', []) if user_data else []

    if not user_words:
        return jsonify({'error': 'Нет слов для тренировки'}), 400

    session_obj = create_training_session(
        words_count=words_count,
        user_words=user_words,
        username=session['username']
    )

    return jsonify({
        'session_id': session_obj['session_id'],
        'total_questions': len(session_obj['words']),
        'words_count': len(session_obj['words'])
    })


@app.route('/api/training/question/<session_id>')
@login_required
def api_get_training_question(session_id):
    from services.training import get_current_question as get_training_question

    question = get_training_question(session_id)
    if question:
        return jsonify(question)
    return jsonify({"finished": True}), 200


@app.route('/api/training/answer', methods=['POST'])
@login_required
def api_training_answer():
    from services.training import submit_answer as submit_training_answer

    data = request.json
    session_id = data.get('session_id')
    word_id = data.get('word_id')
    selected_answer = data.get('answer')

    result = submit_training_answer(session_id, word_id, selected_answer)

    if result.get('finished'):
        correct = result.get('results', {}).get('correct', 0)
        total_xp = correct * 10

        if total_xp > 0:
            user_data = get_user_data(session['username'])
            if user_data:
                user_level = user_data.get('user_level', {'current': 1, 'xp': 0, 'next_level_xp': 100})
                user_level['xp'] = user_level.get('xp', 0) + total_xp

                while user_level['xp'] >= user_level.get('next_level_xp', 100):
                    user_level['xp'] -= user_level.get('next_level_xp', 100)
                    user_level['current'] = user_level.get('current', 1) + 1
                    user_level['next_level_xp'] = int(user_level.get('next_level_xp', 100) * 1.2)

                user_data['user_level'] = user_level
                update_user_words(session['username'], user_data.get('words', []))

    return jsonify(result)


@app.route('/api/training/session/<session_id>/results')
@login_required
def api_get_training_results(session_id):
    from services.training import get_session_results

    results = get_session_results(session_id)
    if results:
        return jsonify(results)
    return jsonify({"error": "Session not found"}), 404


# ===== SRS ENDPOINTS =====

@app.route('/api/srs/notifications')
@login_required
def api_get_srs_notifications():
    due = get_due_notifications(session['username'])
    return jsonify({
        'notifications': due,
        'count': len(due)
    })


@app.route('/api/srs/stats')
@login_required
def api_get_srs_stats():
    stats = get_srs_stats(session['username'])
    return jsonify(stats)


@app.route('/api/srs/upcoming')
@login_required
def api_get_upcoming_reviews():
    days = request.args.get('days', 7, type=int)
    upcoming = get_upcoming_reviews(session['username'], days)
    return jsonify(upcoming)


@app.route('/api/srs/notification/<int:notif_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notif_id):
    success = mark_notification_read(session['username'], notif_id)
    return jsonify({'success': success})


@app.route('/api/srs/notifications/read-all', methods=['POST'])
@login_required
def api_mark_all_read():
    count = mark_all_read(session['username'])
    return jsonify({'marked_read': count})


@app.route('/api/training/srs')
@login_required

def api_start_srs_training():
    """Начать тренировку с словами, которые нужно повторить по SRS (только просроченные)"""
    from services.training import create_training_session, get_due_words_for_review

    user_data = get_user_data(session['username'])
    if not user_data:
        return jsonify({'error': 'Пользователь не найден'}), 400

    user_words = user_data.get('words', [])

    if not user_words:
        return jsonify({'error': 'Нет слов для повторения. Сыграйте в викторину или спринт!'}), 400

    # Получаем ТОЛЬКО просроченные слова (due_now)
    due_words = get_due_words_for_review(session['username'], user_words, max_words=None)

    if not due_words:
        # Проверяем, есть ли запланированные на сегодня
        from services.notifications import get_srs_stats
        stats = get_srs_stats(session['username'])
        if stats.get('due_today', 0) > 0:
            return jsonify({'error': f'Все слова на сегодня уже повторены! Следующие повторения позже.'}), 400
        else:
            return jsonify({'error': 'Нет слов для повторения. Все слова выучены!'}), 400

    # Создаем сессию со ВСЕМИ просроченными словами
    session_obj = create_training_session(
        words_count=len(due_words),
        user_words=due_words,
        username=session['username']
    )

    session_id = session_obj['session_id']
    print(f"[SRS TRAINING] Создана сессия {session_id} с {len(due_words)} просроченными словами")

    return jsonify({
        'success': True,
        'session_id': session_id,
        'words_count': len(due_words),
        'message': f'Найдено {len(due_words)} слов для повторения',
        'redirect_url': f'/srs-train?session={session_id}'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)