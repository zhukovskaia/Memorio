import random
import uuid
from data.words import get_quiz_questions_by_level, get_all_card_questions

active_games = {}


def start_game(game_type, level=1):
    game_id = str(uuid.uuid4())[:8]
    questions = []

    if game_type == 'quiz':
        all_questions = get_quiz_questions_by_level(level)
        questions = random.sample(all_questions, min(len(all_questions), 10))
    elif game_type == 'sprint':
        from data.words import QUIZ_QUESTIONS
        pool = [q for q in QUIZ_QUESTIONS if q.get('level', 1) <= level]
        random.shuffle(pool)
        questions = pool[:100]
    elif game_type == 'cards':
        all_cards = get_all_card_questions()
        questions = random.sample(all_cards, min(len(all_cards), 15))

    active_games[game_id] = {
        'game_id': game_id,
        'game_type': game_type,
        'questions': questions,
        'current_index': 0,
        'answers': [],
        'finished': False,
        'correct_count': 0,
        'wrong_count': 0,
        'combo': 0,
        'streak': 0,
        'combo_active': False,
        'sprint_score': 0
    }
    return game_id


def get_current_question(game_id):
    game = active_games.get(game_id)
    if not game or game['finished']:
        return None
    if game['current_index'] >= len(game['questions']):
        game['finished'] = True
        return None

    current_word = game['questions'][game['current_index']]

    if game['game_type'] == 'cards':
        return {
            "question": current_word.get('word'),
            "answer": current_word.get('translation'),
            "word_id": current_word.get('id'),
            "question_number": game['current_index'] + 1,
            "total_questions": len(game['questions']),
            "type": "flashcard"
        }

    correct_ans = current_word.get('translation')
    other_answers = []
    for q in game['questions']:
        ans = q.get('translation')
        if ans != correct_ans and ans not in other_answers:
            other_answers.append(ans)
    while len(other_answers) < 3:
        other_answers.append("???")
    wrong_options = random.sample(other_answers, 3)
    options = wrong_options + [correct_ans]
    random.shuffle(options)

    return {
        "question": current_word.get('word'),
        "correct_answer": correct_ans,
        "options": options,
        "word_id": current_word.get('id'),
        "question_number": game['current_index'] + 1,
        "total_questions": len(game['questions']),
        "type": "quiz"
    }


def submit_answer(game_id, word_id, selected_answer):
    game = active_games.get(game_id)
    if not game or game['finished']:
        return {"error": "Игра не найдена"}

    # Ищем текущее слово
    current_word = None
    for word in game['questions']:
        if word.get('id') == word_id:
            current_word = word
            break

    if not current_word:
        return {"error": "Вопрос не найден"}

    correct_ans = current_word.get('translation')

    # Для карточек - просто переходим дальше
    if game['game_type'] == 'cards':
        game['current_index'] += 1
        # Сохраняем просмотр как факт
        game['answers'].append({
            'word_id': word_id,
            'word': current_word.get('word'),
            'is_correct': None,
            'user_answer': 'viewed',
            'correct_answer': correct_ans
        })
        return {"finished": game['current_index'] >= len(game['questions']), "type": "cards"}

    is_correct = (selected_answer == correct_ans)

    # Сохраняем ответ с полной информацией
    game['answers'].append({
        'word_id': word_id,
        'word': current_word.get('word'),
        'is_correct': is_correct,
        'user_answer': selected_answer,
        'correct_answer': correct_ans
    })

    game['current_index'] += 1

    if game['game_type'] == 'sprint':
        if is_correct:
            game['correct_count'] += 1
            game['streak'] += 1
            if game['streak'] >= 5:
                game['combo_active'] = True
            points = 4 if game['combo_active'] else 2
            game['sprint_score'] += points
        else:
            game['wrong_count'] += 1
            game['streak'] = 0
            game['combo_active'] = False

        return {
            "is_correct": is_correct,
            "correct_answer": correct_ans,
            "sprint_score": game['sprint_score'],
            "streak": game['streak'],
            "combo_active": game['combo_active']
        }

    if is_correct:
        game['correct_count'] += 1
        game['combo'] += 1
    else:
        game['wrong_count'] += 1
        game['combo'] = 0

    is_finished = game['current_index'] >= len(game['questions'])
    xp_earned = 0
    if is_correct:
        xp_earned = 5
        if game['game_type'] == 'sprint':
            xp_earned += game['combo'] * 2

    if is_finished:
        game['finished'] = True
        return {
            "is_correct": is_correct,
            "correct_answer": correct_ans,
            "finished": True,
            "xp_earned": xp_earned,
            "results": {
                "correct": game['correct_count'],
                "wrong": game['wrong_count'],
                "total": len(game['questions']),
                "xp_earned": game['correct_count'] * 5
            }
        }
    return {
        "is_correct": is_correct,
        "correct_answer": correct_ans,
        "finished": False,
        "xp_earned": xp_earned,
        "combo": game['combo']
    }


def finish_sprint(game_id):
    game = active_games.get(game_id)
    if not game:
        return None
    game['finished'] = True
    return {
        "sprint_score": game['sprint_score'],
        "correct": game['correct_count'],
        "wrong": game['wrong_count']
    }


def get_game_results(game_id):
    game = active_games.get(game_id)
    if not game:
        return None
    return {
        "correct": game['correct_count'],
        "wrong": game['wrong_count'],
        "total": len(game['questions']),
        "xp_earned": game['correct_count'] * 5
    }