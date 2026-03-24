from flask import Flask, render_template, request, jsonify
import os

from data.words import get_all_words, update_card_stats, get_word_by_id
from services.training import (
    create_training_session,
    get_current_question,
    submit_answer,
    get_session_results
)
from services.statistics import calculate_progress

app = Flask(__name__)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/study')
def study():
    """Страница тренировки"""
    return render_template('study.html')


@app.route('/api/training/start', methods=['POST'])
def api_start_training():
    """Начать новую тренировку"""
    data = request.json
    words_count = data.get('count', 10)

    session = create_training_session(words_count)

    return jsonify({
        "session_id": session['session_id'],
        "total_questions": len(session['words'])
    })


@app.route('/api/training/question/<session_id>')
def api_get_question(session_id):
    """Получить следующий вопрос"""
    question = get_current_question(session_id)
    if question:
        return jsonify(question)
    else:
        return jsonify({"finished": True}), 200


@app.route('/api/training/answer', methods=['POST'])
def api_check_answer():
    """Проверить ответ"""
    data = request.json
    session_id = data.get('session_id')
    word_id = data.get('word_id')
    selected_answer = data.get('answer')

    result = submit_answer(session_id, word_id, selected_answer)
    return jsonify(result)


@app.route('/api/training/session/<session_id>/results')
def api_get_results(session_id):
    """Получить результаты сессии"""
    results = get_session_results(session_id)
    if results:
        return jsonify(results)
    else:
        return jsonify({"error": "Session not found"}), 404


@app.route('/api/stats')
def api_get_stats():
    """Получить общую статистику"""
    words = get_all_words()
    stats = calculate_progress(words)
    return jsonify(stats)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)