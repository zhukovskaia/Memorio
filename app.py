from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from functools import wraps
from services.games import start_game, get_current_question, submit_answer, get_game_results, finish_sprint
from auth.user_manager import (
    register_user, login_user, get_user_data, update_user_words,
    get_user_level, get_game_progress, update_game_progress, add_account_points,
    update_sprint_record, get_user_stats, update_global_stats
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
    if question: return jsonify(question)
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

        # 1. Обновляем прогресс игры (XP игры)
        if game_name != 'cards':
            _, game = update_game_progress(session['username'], game_name, xp_earned)
            result['game_progress'] = game

        # 2. Добавляем баллы на АККАУНТ (Растет уровень аккаунта)
        # За Викторину начисляем полученные очки опыта как баллы аккаунта
        if game_name == 'quiz':
            add_account_points(session['username'], xp_earned)

        # 3. Обновляем статистику
        if game_name == 'quiz':
            correct = result.get('results', {}).get('correct', 0)
            wrong = result.get('results', {}).get('wrong', 0)
            update_global_stats(session['username'], 'quiz', correct, wrong)

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
        # Обновляем рекорд
        update_sprint_record(session['username'], result['correct'])

        # Добавляем баллы на аккаунт (равно количеству очков, набранных в спринте)
        add_account_points(session['username'], result['sprint_score'])

        # Обновляем статистику
        update_global_stats(session['username'], 'sprint', result['correct'], result['wrong'])

        result['account_points_earned'] = result['sprint_score']

    return jsonify(result)


@app.route('/api/user/stats')
@login_required
def api_user_stats():
    return jsonify(get_user_stats(session['username']))


@app.route('/api/game/<game_id>/results')
@login_required
def api_get_game_results(game_id):
    results = get_game_results(game_id)
    if results: return jsonify(results)
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)