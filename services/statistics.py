def calculate_progress(words):
    """Рассчитать прогресс по всем словам"""
    total_correct = sum(w['correct'] for w in words)
    total_wrong = sum(w['wrong'] for w in words)
    total_attempts = total_correct + total_wrong
    success_rate = 0
    if total_attempts > 0:
        success_rate = round((total_correct / total_attempts) * 100)

    easy = 0
    medium = 0
    hard = 0
    new = 0

    for word in words:
        total = word['correct'] + word['wrong']
        if total == 0:
            new += 1
        elif word['correct'] / total >= 0.8:
            easy += 1
        elif word['correct'] / total >= 0.5:
            medium += 1
        else:
            hard += 1

    return {
        "total_cards": len(words),
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "total_attempts": total_attempts,
        "success_rate": success_rate,
        "difficulty": {
            "new": new,
            "easy": easy,
            "medium": medium,
            "hard": hard
        }
    }

def get_word_stats(word):
    """Получить статистику по одному слову"""
    total = word['correct'] + word['wrong']
    difficulty = "new"
    if total > 0:
        if word['correct'] / total >= 0.8:
            difficulty = "easy"
        elif word['correct'] / total >= 0.5:
            difficulty = "medium"
        else:
            difficulty = "hard"

    return {
        "id": word['id'],
        "word": word['word'],
        "translation": word['translation'],
        "correct": word['correct'],
        "wrong": word['wrong'],
        "total_attempts": total,
        "success_rate": round((word['correct'] / total * 100) if total > 0 else 0),
        "difficulty": difficulty
    }