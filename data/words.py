import json
import os
import random
from datetime import datetime
DATA_FILE = os.path.join(os.path.dirname(__file__), 'words_data.json')

# ==========================================
# БАЗА ДЛЯ ВИКТОРИНЫ (Смешанные типы: Теория + Практика)
# ==========================================
QUIZ_QUESTIONS = [
    # --- УРОВЕНЬ 1 (База) ---
    {"id": 101, "word": "print('Hello')", "translation": "Hello", "level": 1, "type": "code"},
    {"id": 102, "word": "type(5)", "translation": "<class 'int'>", "level": 1, "type": "theory"},
    {"id": 103, "word": "int('10') + 5", "translation": "15", "level": 1, "type": "code"},
    {"id": 104, "word": "Создание переменной", "translation": "x = 10", "level": 1, "type": "theory"},
    {"id": 105, "word": "10 // 3", "translation": "3", "level": 1, "type": "code"},
    {"id": 106, "word": "Логический тип", "translation": "bool", "level": 1, "type": "theory"},
    {"id": 107, "word": "'A' + 'B'", "translation": "AB", "level": 1, "type": "code"},
    {"id": 108, "word": "Комментарий в коде", "translation": "#", "level": 1, "type": "theory"},
    {"id": 109, "word": "len('Python')", "translation": "6", "level": 1, "type": "code"},
    {"id": 110, "word": "Функция ввода", "translation": "input()", "level": 1, "type": "theory"},
    {"id": 111, "word": "True and False", "translation": "False", "level": 1, "type": "code"},
    {"id": 112, "word": "Оператор присваивания", "translation": "=", "level": 1, "type": "theory"},
    {"id": 113, "word": "str(100)", "translation": "'100'", "level": 1, "type": "code"},
    {"id": 114, "word": "Список пустой", "translation": "[]", "level": 1, "type": "theory"},
    {"id": 115, "word": "2 ** 3", "translation": "8", "level": 1, "type": "code"},
    {"id": 116, "word": "Булевы значения", "translation": "True, False", "level": 1, "type": "theory"},
    {"id": 117, "word": "x = 5; x += 2", "translation": "7", "level": 1, "type": "code"},
    {"id": 118, "word": "Сравнение на равенство", "translation": "==", "level": 1, "type": "theory"},
    {"id": 119, "word": "print(1, 2)", "translation": "1 2", "level": 1, "type": "code"},
    {"id": 120, "word": "Сравнение на неравенство", "translation": "!=", "level": 1, "type": "theory"},
    {"id": 121, "word": "10 % 3", "translation": "1", "level": 1, "type": "code"},
    {"id": 122, "word": "Список обозначается через", "translation": "[]", "level": 1, "type": "theory"},
    {"id": 123, "word": "bool('')", "translation": "False", "level": 1, "type": "code"},
    {"id": 124, "word": "Оператор 'или'", "translation": "or", "level": 1, "type": "theory"},
    {"id": 125, "word": "float(5)", "translation": "5.0", "level": 1, "type": "code"},
    {"id": 126, "word": "Оператор 'и'", "translation": "and", "level": 1, "type": "theory"},
    {"id": 127, "word": "int(True)", "translation": "1", "level": 1, "type": "code"},
    {"id": 128, "word": "None обозначает", "translation": "Пустоту", "level": 1, "type": "theory"},
    {"id": 129, "word": "int(False)", "translation": "0", "level": 1, "type": "code"},
    {"id": 130, "word": "Кортеж пустой", "translation": "()", "level": 1, "type": "theory"},

    # --- УРОВЕНЬ 2 (Строки и Условия) ---
    {"id": 201, "word": "'Python'[0]", "translation": "P", "level": 2, "type": "code"},
    {"id": 202, "word": "Срез строки", "translation": "[start:stop]", "level": 2, "type": "theory"},
    {"id": 203, "word": "'abc'.upper()", "translation": "ABC", "level": 2, "type": "code"},
    {"id": 204, "word": "Условный оператор", "translation": "if", "level": 2, "type": "theory"},
    {"id": 205, "word": "for i in range(3): print(i)", "translation": "0 1 2", "level": 2, "type": "code"},
    {"id": 206, "word": "Цикл с условием", "translation": "while", "level": 2, "type": "theory"},
    {"id": 207, "word": "break в цикле", "translation": "Прерывает цикл", "level": 2, "type": "theory"},
    {"id": 208, "word": "'a' in 'abc'", "translation": "True", "level": 2, "type": "code"},
    {"id": 209, "word": "Функция длины", "translation": "len()", "level": 2, "type": "theory"},
    {"id": 210, "word": "[1, 2][0]", "translation": "1", "level": 2, "type": "code"},
    {"id": 211, "word": "Максимум из списка", "translation": "max()", "level": 2, "type": "theory"},
    {"id": 212, "word": "sorted([3, 1, 2])", "translation": "[1, 2, 3]", "level": 2, "type": "code"},
    {"id": 213, "word": "Сумма элементов", "translation": "sum()", "level": 2, "type": "theory"},
    {"id": 214, "word": "f'Hi {name}'", "translation": "f-строка", "level": 2, "type": "theory"},
    {"id": 215, "word": "round(3.6)", "translation": "4", "level": 2, "type": "code"},
    {"id": 216, "word": "Абсолютное число", "translation": "abs()", "level": 2, "type": "theory"},
    {"id": 217, "word": "pow(2, 3)", "translation": "8", "level": 2, "type": "code"},
    {"id": 218, "word": "Степень числа", "translation": "**", "level": 2, "type": "theory"},
    {"id": 219, "word": "divmod(10, 3)", "translation": "(3, 1)", "level": 2, "type": "code"},
    {"id": 220, "word": "Остаток от деления", "translation": "%", "level": 2, "type": "theory"},
    {"id": 221, "word": "bool('False')", "translation": "True", "level": 2, "type": "code"},
    {"id": 222, "word": "Конкатенация строк", "translation": "+", "level": 2, "type": "theory"},
    {"id": 223, "word": "'-'.join(['a', 'b'])", "translation": "a-b", "level": 2, "type": "code"},
    {"id": 224, "word": "Разделение строки", "translation": ".split()", "level": 2, "type": "theory"},
    {"id": 225, "word": "' a '.strip()", "translation": "a", "level": 2, "type": "code"},
    {"id": 226, "word": "Удаление пробелов", "translation": ".strip()", "level": 2, "type": "theory"},
    {"id": 227, "word": "x = [1, 2]; x.pop()", "translation": "2", "level": 2, "type": "code"},
    {"id": 228, "word": "Удаление элемента списка", "translation": ".pop()", "level": 2, "type": "theory"},
    {"id": 229, "word": "x = [1, 2]; x.append(3)", "translation": "[1, 2, 3]", "level": 2, "type": "code"},
    {"id": 230, "word": "Добавление в список", "translation": ".append()", "level": 2, "type": "theory"},

    # --- УРОВЕНЬ 3 (Списки, Словари, Функции) ---
    {"id": 301, "word": "d = {'a': 1}; d['a']", "translation": "1", "level": 3, "type": "code"},
    {"id": 302, "word": "Пара ключ-значение", "translation": "dict (словарь)", "level": 3, "type": "theory"},
    {"id": 303, "word": "def f(): pass", "translation": "Пустая функция", "level": 3, "type": "code"},
    {"id": 304, "word": "Возврат из функции", "translation": "return", "level": 3, "type": "theory"},
    {"id": 305, "word": "[x*2 for x in [1, 2]]", "translation": "[2, 4]", "level": 3, "type": "code"},
    {"id": 306, "word": "Генератор списка", "translation": "[... for ...]", "level": 3, "type": "theory"},
    {"id": 307, "word": "set([1, 1, 2])", "translation": "{1, 2}", "level": 3, "type": "code"},
    {"id": 308, "word": "Множество уникальных", "translation": "set", "level": 3, "type": "theory"},
    {"id": 309, "word": "t = (1, 2); t[0] = 5", "translation": "Ошибка", "level": 3, "type": "code"},
    {"id": 310, "word": "Неизменяемый список", "translation": "tuple (кортеж)", "level": 3, "type": "theory"},
    {"id": 311, "word": "global x", "translation": "Глобальная переменная", "level": 3, "type": "theory"},
    {"id": 312, "word": "x = [1, 2]; y = x", "translation": "Ссылка на объект", "level": 3, "type": "theory"},
    {"id": 313, "word": "x = [1, 2]; y = x[:]", "translation": "Копия списка", "level": 3, "type": "theory"},
    {"id": 314, "word": "lambda x: x + 1", "translation": "Анонимная функция", "level": 3, "type": "theory"},
    {"id": 315, "word": "enumerate(['a', 'b'])", "translation": "(0, 'a'), (1, 'b')", "level": 3, "type": "code"},
    {"id": 316, "word": "Нумерация списка", "translation": "enumerate()", "level": 3, "type": "theory"},
    {"id": 317, "word": "zip([1], ['a'])", "translation": "(1, 'a')", "level": 3, "type": "code"},
    {"id": 318, "word": "Объединение списков", "translation": "zip()", "level": 3, "type": "theory"},
    {"id": 319, "word": "map(int, ['1'])", "translation": "Применение функции", "level": 3, "type": "theory"},
    {"id": 320, "word": "filter(bool, [0, 1])", "translation": "Фильтрация", "level": 3, "type": "theory"},
    {"id": 321, "word": "try: 1/0 except: print('E')", "translation": "E", "level": 3, "type": "code"},
    {"id": 322, "word": "Обработка ошибок", "translation": "try/except", "level": 3, "type": "theory"},
    {"id": 323, "word": "raise ValueError", "translation": "Выброс исключения", "level": 3, "type": "theory"},
    {"id": 324, "word": "assert 1 == 2", "translation": "AssertionError", "level": 3, "type": "code"},
    {"id": 325, "word": "Проверка утверждения", "translation": "assert", "level": 3, "type": "theory"},
    {"id": 326, "word": "open('file.txt')", "translation": "Открытие файла", "level": 3, "type": "theory"},
    {"id": 327, "word": "f.read()", "translation": "Чтение файла", "level": 3, "type": "theory"},
    {"id": 328, "word": "with open(...) as f:", "translation": "Контекстный менеджер", "level": 3, "type": "theory"},
    {"id": 329, "word": "import math", "translation": "Импорт модуля", "level": 3, "type": "theory"},
    {"id": 330, "word": "from math import pi", "translation": "Импорт имени", "level": 3, "type": "theory"},

    # --- УРОВЕНЬ 4 (Продвинутый) ---
    {"id": 401, "word": "print(1, 2, sep='-')", "translation": "1-2", "level": 4, "type": "code"},
    {"id": 402, "word": "Разделитель print", "translation": "sep=", "level": 4, "type": "theory"},
    {"id": 403, "word": "print(1, end='!')", "translation": "1!", "level": 4, "type": "code"},
    {"id": 404, "word": "Конец строки print", "translation": "end=", "level": 4, "type": "theory"},
    {"id": 405, "word": "{x: x**2 for x in [1]}", "translation": "{1: 1}", "level": 4, "type": "code"},
    {"id": 406, "word": "Генератор словаря", "translation": "{k: v for ...}", "level": 4, "type": "theory"},
    {"id": 407, "word": "getattr(obj, 'name')", "translation": "Получить атрибут", "level": 4, "type": "theory"},
    {"id": 408, "word": "hasattr(obj, 'name')", "translation": "Проверить атрибут", "level": 4, "type": "theory"},
    {"id": 409, "word": "isinstance(5, int)", "translation": "True", "level": 4, "type": "code"},
    {"id": 410, "word": "Проверка типа", "translation": "isinstance()", "level": 4, "type": "theory"},
    {"id": 411, "word": "a, b = b, a", "translation": "Обмен значениями", "level": 4, "type": "theory"},
    {"id": 412, "word": "x = 10; y = 5", "translation": "Присваивание", "level": 4, "type": "theory"},
    {"id": 413, "word": "x = 5; y = 5; x is y", "translation": "True", "level": 4, "type": "code"},
    {"id": 414, "word": "Сравнение объектов", "translation": "is", "level": 4, "type": "theory"},
    {"id": 415, "word": "eval('2 + 2')", "translation": "4", "level": 4, "type": "code"},
    {"id": 416, "word": "Выполнение строки", "translation": "eval()", "level": 4, "type": "theory"},
    {"id": 417, "word": "exec('x = 5')", "translation": "Выполняет код", "level": 4, "type": "theory"},
    {"id": 418, "word": "def f(*args):", "translation": "Кортеж аргументов", "level": 4, "type": "theory"},
    {"id": 419, "word": "def f(**kwargs):", "translation": "Словарь аргументов", "level": 4, "type": "theory"},
    {"id": 420, "word": "x = [1]; y = [1]; x is y", "translation": "False", "level": 4, "type": "code"},
    {"id": 421, "word": "Разные объекты в памяти", "translation": "False (is)", "level": 4, "type": "theory"},
    {"id": 422, "word": "nonlocal x", "translation": "Замыкание", "level": 4, "type": "theory"},
    {"id": 423, "word": "def f(x=[]): ...", "translation": "Опасный default", "level": 4, "type": "theory"},
    {"id": 424, "word": "del x", "translation": "Удаление переменной", "level": 4, "type": "theory"},
    {"id": 425, "word": "pass", "translation": "Ничего не делает", "level": 4, "type": "theory"},
    {"id": 426, "word": "Ellipsis (...)", "translation": "Заглушка", "level": 4, "type": "theory"},
    {"id": 427, "word": "x = 1; def f(): x = 2", "translation": "Локальная переменная", "level": 4, "type": "theory"},
    {"id": 428, "word": "f.readline()", "translation": "Читать строку", "level": 4, "type": "theory"},
    {"id": 429, "word": "open('f', 'r')", "translation": "Чтение", "level": 4, "type": "theory"},
    {"id": 430, "word": "open('f', 'w')", "translation": "Запись (перезапись)", "level": 4, "type": "theory"},

    # --- УРОВЕНЬ 5 (Эксперт) ---
    {"id": 501, "word": "class A: pass", "translation": "Создание класса", "level": 5, "type": "code"},
    {"id": 502, "word": "ООП в Python", "translation": "Классы и Объекты", "level": 5, "type": "theory"},
    {"id": 503, "word": "def __init__(self):", "translation": "Конструктор", "level": 5, "type": "theory"},
    {"id": 504, "word": "self в методе", "translation": "Ссылка на объект", "level": 5, "type": "theory"},
    {"id": 505, "word": "class B(A): pass", "translation": "Наследование", "level": 5, "type": "theory"},
    {"id": 506, "word": "super().method()", "translation": "Метод родителя", "level": 5, "type": "theory"},
    {"id": 507, "word": "@property", "translation": "Геттер", "level": 5, "type": "theory"},
    {"id": 508, "word": "@staticmethod", "translation": "Статический метод", "level": 5, "type": "theory"},
    {"id": 509, "word": "yield", "translation": "Генератор", "level": 5, "type": "theory"},
    {"id": 510, "word": "next(gen)", "translation": "След. значение", "level": 5, "type": "theory"},
    {"id": 511, "word": "def wrapper(f): ...", "translation": "Декоратор", "level": 5, "type": "theory"},
    {"id": 512, "word": "__name__ == '__main__'", "translation": "Точка входа", "level": 5, "type": "theory"},
    {"id": 513, "word": "if __name__ == ...", "translation": "Защита от импорта", "level": 5, "type": "theory"},
    {"id": 514, "word": "x = []; x.append(x)", "translation": "Рекурсия ссылки", "level": 5, "type": "theory"},
    {"id": 515, "word": "__str__ метод", "translation": "Строковое предст.", "level": 5, "type": "theory"},
    {"id": 516, "word": "__repr__ метод", "translation": "Офиц. представление", "level": 5, "type": "theory"},
    {"id": 517, "word": "__len__ метод", "translation": "Длина объекта", "level": 5, "type": "theory"},
    {"id": 518, "word": "__getitem__", "translation": "Индексация obj[i]", "level": 5, "type": "theory"},
    {"id": 519, "word": "iter([1, 2])", "translation": "Создает итератор", "level": 5, "type": "theory"},
    {"id": 520, "word": "StopIteration", "translation": "Конец итератора", "level": 5, "type": "theory"},
    {"id": 521, "word": "with open(...) as f:", "translation": "Авто-закрытие", "level": 5, "type": "theory"},
    {"id": 522, "word": "lambda x: x*2", "translation": "Анонимная функция", "level": 5, "type": "theory"},
    {"id": 523, "word": "map, filter", "translation": "Функции высшего порядка", "level": 5, "type": "theory"},
    {"id": 524, "word": "try/except/finally", "translation": "Блок очистки", "level": 5, "type": "theory"},
    {"id": 525, "word": "assert", "translation": "Отладочное утверждение", "level": 5, "type": "theory"},
    {"id": 526, "word": "raise", "translation": "Генерация исключения", "level": 5, "type": "theory"},
    {"id": 527, "word": "import ... as ...", "translation": "Псевдоним модуля", "level": 5, "type": "theory"},
    {"id": 528, "word": "from ... import ...", "translation": "Импорт конкретного", "level": 5, "type": "theory"},
    {"id": 529, "word": "__init__.py", "translation": "Инициализация пакета", "level": 5, "type": "theory"},
    {"id": 530, "word": "pip install ...", "translation": "Установка пакета", "level": 5, "type": "theory"},
]

# ==========================================
# БАЗА ДЛЯ КАРТОЧЕК (Уровни 1-5)
# ==========================================
CARD_QUESTIONS = [
    # Уровень 1
    {"id": 601, "word": "Переменная", "translation": "Именованная область памяти", "level": 1},
    {"id": 602, "word": "Функция", "translation": "Блок кода с именем", "level": 1},
    {"id": 603, "word": "Список", "translation": "[] - изменяемая коллекция", "level": 1},
    {"id": 604, "word": "Кортеж", "translation": "() - неизменяемая коллекция", "level": 1},
    {"id": 605, "word": "Словарь", "translation": "{} - ключ: значение", "level": 1},
    {"id": 606, "word": "Цикл", "translation": "Повторение действий", "level": 1},
    {"id": 607, "word": "Условие", "translation": "Проверка истинности (if)", "level": 1},
    {"id": 608, "word": "print()", "translation": "Вывод данных на экран", "level": 1},
    {"id": 609, "word": "input()", "translation": "Ввод данных пользователем", "level": 1},
    {"id": 610, "word": "int()", "translation": "Целое число", "level": 1},
    {"id": 611, "word": "str()", "translation": "Строка (текст)", "level": 1},
    {"id": 612, "word": "bool()", "translation": "Логический тип (True/False)", "level": 1},
    {"id": 613, "word": "None", "translation": "Пустое значение", "level": 1},
    {"id": 614, "word": "#", "translation": "Комментарий", "level": 1},
    {"id": 615, "word": "=", "translation": "Оператор присваивания", "level": 1},
    # Уровень 2
    {"id": 616, "word": "len()", "translation": "Длина объекта", "level": 2},
    {"id": 617, "word": "range()", "translation": "Генератор чисел", "level": 2},
    {"id": 618, "word": "append()", "translation": "Добавить в конец списка", "level": 2},
    {"id": 619, "word": "split()", "translation": "Разбить строку на список", "level": 2},
    {"id": 620, "word": "join()", "translation": "Собрать список в строку", "level": 2},
    {"id": 621, "word": "strip()", "translation": "Убрать пробелы по краям", "level": 2},
    {"id": 622, "word": "upper()", "translation": "ВСЕ ЗАГЛАВНЫЕ", "level": 2},
    {"id": 623, "word": "lower()", "translation": "все строчные", "level": 2},
    {"id": 624, "word": "max()", "translation": "Максимальный элемент", "level": 2},
    {"id": 625, "word": "min()", "translation": "Минимальный элемент", "level": 2},
    {"id": 626, "word": "sum()", "translation": "Сумма элементов", "level": 2},
    {"id": 627, "word": "break", "translation": "Прервать цикл", "level": 2},
    {"id": 628, "word": "continue", "translation": "Пропустить итерацию", "level": 2},
    {"id": 629, "word": "in", "translation": "Проверка вхождения", "level": 2},
    {"id": 630, "word": "and/or", "translation": "Логические операторы", "level": 2},
    # Уровень 3
    {"id": 631, "word": "def", "translation": "Определение функции", "level": 3},
    {"id": 632, "word": "return", "translation": "Вернуть результат", "level": 3},
    {"id": 633, "word": "lambda", "translation": "Анонимная функция", "level": 3},
    {"id": 634, "word": "map()", "translation": "Применить функцию ко всем", "level": 3},
    {"id": 635, "word": "filter()", "translation": "Отфильтровать элементы", "level": 3},
    {"id": 636, "word": "enumerate()", "translation": "Индекс + Значение", "level": 3},
    {"id": 637, "word": "zip()", "translation": "Объединить списки", "level": 3},
    {"id": 638, "word": "set()", "translation": "Множество (уникальные)", "level": 3},
    {"id": 639, "word": "try/except", "translation": "Обработка ошибок", "level": 3},
    {"id": 640, "word": "raise", "translation": "Создать ошибку", "level": 3},
    {"id": 641, "word": "global", "translation": "Глобальная переменная", "level": 3},
    {"id": 642, "word": "nonlocal", "translation": "Внешняя переменная", "level": 3},
    {"id": 643, "word": "import", "translation": "Подключить модуль", "level": 3},
    {"id": 644, "word": "as", "translation": "Псевдоним", "level": 3},
    {"id": 645, "word": "with", "translation": "Контекстный менеджер", "level": 3},
    # Уровень 4
    {"id": 646, "word": "class", "translation": "Создание класса", "level": 4},
    {"id": 647, "word": "self", "translation": "Ссылка на экземпляр", "level": 4},
    {"id": 648, "word": "__init__", "translation": "Конструктор класса", "level": 4},
    {"id": 649, "word": "inheritance", "translation": "Наследование", "level": 4},
    {"id": 650, "word": "super()", "translation": "Вызов родителя", "level": 4},
    {"id": 651, "word": "@property", "translation": "Свойство (геттер)", "level": 4},
    {"id": 652, "word": "@staticmethod", "translation": "Статический метод", "level": 4},
    {"id": 653, "word": "yield", "translation": "Генератор (пауза)", "level": 4},
    {"id": 654, "word": "decorator", "translation": "Обертка для функции", "level": 4},
    {"id": 655, "word": "args/kwargs", "translation": "Переменное кол-во аргументов", "level": 4},
    {"id": 656, "word": "isinstance()", "translation": "Проверка типа", "level": 4},
    {"id": 657, "word": "is", "translation": "Сравнение объектов (id)", "level": 4},
    {"id": 658, "word": "copy()", "translation": "Поверхностная копия", "level": 4},
    {"id": 659, "word": "deepcopy()", "translation": "Глубокая копия", "level": 4},
    {"id": 660, "word": "eval()", "translation": "Выполнить строку как код", "level": 4},
    # Уровень 5
    {"id": 661, "word": "__str__", "translation": "Человеко-читаемая строка", "level": 5},
    {"id": 662, "word": "__repr__", "translation": "Официальная строка", "level": 5},
    {"id": 663, "word": "__len__", "translation": "Длина объекта", "level": 5},
    {"id": 664, "word": "__getitem__", "translation": "Индексация obj[i]", "level": 5},
    {"id": 665, "word": "iter()", "translation": "Создать итератор", "level": 5},
    {"id": 666, "word": "next()", "translation": "Следующий элемент", "level": 5},
    {"id": 667, "word": "StopIteration", "translation": "Конец итерации", "level": 5},
    {"id": 668, "word": "assert", "translation": "Проверка (для отладки)", "level": 5},
    {"id": 669, "word": "pass", "translation": "Заглушка (ничего)", "level": 5},
    {"id": 670, "word": "del", "translation": "Удалить объект", "level": 5},
    {"id": 671, "word": "exec()", "translation": "Выполнить блок кода", "level": 5},
    {"id": 672, "word": "getattr()", "translation": "Получить атрибут", "level": 5},
    {"id": 673, "word": "setattr()", "translation": "Установить атрибут", "level": 5},
    {"id": 674, "word": "hasattr()", "translation": "Есть ли атрибут", "level": 5},
    {"id": 675, "word": "dir()", "translation": "Список атрибутов", "level": 5},
    {"id": 676, "word": "id()", "translation": "Адрес в памяти", "level": 5},
    {"id": 677, "word": "type()", "translation": "Тип объекта", "level": 5},
    {"id": 678, "word": "help()", "translation": "Документация", "level": 5},
    {"id": 679, "word": "pip", "translation": "Менеджер пакетов", "level": 5},
    {"id": 680, "word": "venv", "translation": "Виртуальное окружение", "level": 5},
]

def _load_words():
    # Заглушка для совместимости, если где-то вызывают
    return CARD_QUESTIONS

def get_quiz_questions_by_level(level):
    """Получить вопросы для викторины по уровню (теория + практика)"""
    filtered = [q for q in QUIZ_QUESTIONS if q.get('level', 1) <= level]
    return filtered

def get_all_card_questions():
    """Получить ВСЕ вопросы для режима Карточки (все уровни)"""
    return CARD_QUESTIONS


def update_card_stats(word_id, is_correct):
    """Обновить статистику слова в words_data.json"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            words = json.load(f)

        for word in words:
            if word['id'] == word_id:
                if is_correct:
                    word['correct'] = word.get('correct', 0) + 1
                    word['srs_streak'] = word.get('srs_streak', 0) + 1
                else:
                    word['wrong'] = word.get('wrong', 0) + 1
                    word['srs_streak'] = max(0, word.get('srs_streak', 0) - 1)

                word['last_reviewed'] = datetime.now().isoformat()

                # Рассчитываем следующую дату повторения
                from services.notifications import get_next_review_date
                next_review = get_next_review_date(
                    word.get('srs_streak', 0),
                    is_correct
                )
                word['next_review'] = next_review.isoformat()
                break

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Error updating card stats: {e}")
        return False

def get_random_words(count=10, difficulty=None):
    return random.sample(CARD_QUESTIONS, min(count, len(CARD_QUESTIONS)))