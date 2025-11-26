# backend/main.py основной файл с эндпоинтами FastAPI
import random
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import CompileRequest, AssessRequest, AntiCheatEvent, AntiCheatAnalyze  # CompileResponse/AssessResponse можно не использовать жёстко
from sandbox import run_js, run_py
from llm_client import analyze_code, analyze_anti_cheat
from report import generate_report

app = FastAPI()

# -------------------------------------------------
# CORS (для фронта)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# БАНК ЗАДАНИЙ
# -------------------------------------------------
TASK_BANK_JS: Dict[str, List[Dict[str, Any]]] = {

    # EASY — базовые задачи
    "easy": [
        {
            "id": "easy-1",
            "title": "Сортировка массива чисел",
            "description": (
                "Реализуйте функцию sortNumbers(arr), которая принимает массив чисел "
                "и возвращает новый массив, отсортированный по возрастанию. "
                "Нельзя использовать arr.sort()."
            ),
            "template": "function sortNumbers(arr) {\n  // Реализуйте сортировку вручную\n}\n",
        },
        {
            "id": "easy-2",
            "title": "Поиск минимального значения",
            "description": (
                "Напишите функцию minArr(arr), которая возвращает самое маленькое число в массиве. "
                "Решить без Math.min(...arr)."
            ),
            "template": "function minArr(arr) {\n  // Найдите минимум вручную\n}\n",
        },
        {
            "id": "easy-3",
            "title": "Подсчёт количества слов",
            "description": (
                "Создайте функцию countWords(str), которая принимает строку и возвращает "
                "количество слов в ней. Считайте, что слова разделяются одним пробелом."
            ),
            "template": "function countWords(str) {\n  // Подсчитайте количество слов\n}\n",
        },
        {
            "id": "easy-4",
            "title": "Проверка строки на палиндром",
            "description": (
                "Реализуйте функцию isPalindrome(str), которая проверяет, является ли строка "
                "палиндромом (одинаково читается слева направо и справа налево). Игнорируйте регистр."
            ),
            "template": "function isPalindrome(str) {\n  // Проверьте строку\n}\n",
        },
        {
            "id": "easy-5",
            "title": "Удаление дубликатов",
            "description": (
                "Напишите функцию removeDuplicates(arr), которая удаляет повторяющиеся элементы массива "
                "и возвращает новый массив только с уникальными значениями (сохраните порядок первых вхождений)."
            ),
            "template": "function removeDuplicates(arr) {\n  // Удалите дубликаты вручную\n}\n",
        },
        {
            "id": "easy-6",
            "title": "Сумма цифр числа",
            "description": (
                "Напишите функцию sumDigits(num), которая возвращает сумму всех цифр числа. "
                "Учтите, что num может быть отрицательным."
            ),
            "template": "function sumDigits(num) {\n  // Разбейте число на цифры и просуммируйте\n}\n",
        },
        {
            "id": "easy-7",
            "title": "Реверс массива",
            "description": (
                "Реализуйте функцию reverseArray(arr), которая возвращает новый массив "
                "с элементами в обратном порядке. Не используйте встроенный reverse()."
            ),
            "template": "function reverseArray(arr) {\n  // Переверните массив вручную\n}\n",
        },
        {
            "id": "easy-8",
            "title": "Фильтрация чётных чисел",
            "description": (
                "Создайте функцию filterEven(arr), возвращающую массив только из чётных чисел. "
                "Нечётные числа должны быть отброшены."
            ),
            "template": "function filterEven(arr) {\n  // Верните только чётные значения\n}\n",
        },
        {
            "id": "easy-9",
            "title": "Подсчёт гласных в строке",
            "description": (
                "Реализуйте функцию countVowels(str), возвращающую количество гласных букв в строке. "
                "Считайте гласными: a, e, i, o, u, а, е, ё, и, о, у, ы, э, ю, я."
            ),
            "template": "function countVowels(str) {\n  // Подсчитайте гласные\n}\n",
        },
        {
            "id": "easy-10",
            "title": "Частотный словарь массива",
            "description": (
                "Создайте функцию freq(arr), которая возвращает объект, где каждому "
                "элементу массива соответствует количество его вхождений."
            ),
            "template": "function freq(arr) {\n  // Верните объект вида {value: count}\n}\n",
        },
    ],

    # MEDIUM — структуры данных, строки, алгоритмы
    "medium": [
        {
            "id": "med-1",
            "title": "Группировка объектов по полю",
            "description": (
                "Реализуйте функцию groupBy(arr, key), которая группирует объекты массива arr "
                "по значению поля key. Результат — объект, где ключи это значения key, "
                "а значения — массивы объектов."
            ),
            "template": "function groupBy(arr, key) {\n  // Сгруппируйте элементы по ключу\n}\n",
        },
        {
            "id": "med-2",
            "title": "Проверка сбалансированности скобок",
            "description": (
                "Напишите функцию isBalanced(str), которая проверяет корректность скобок. "
                "Поддерживаемые скобки: (), {}, []. Используйте стек."
            ),
            "template": "function isBalanced(str) {\n  // Используйте стек\n}\n",
        },
        {
            "id": "med-3",
            "title": "Функция-кешер",
            "description": (
                "Реализуйте функцию memoize(fn), которая возвращает кешированную версию fn. "
                "Если fn уже вызывали с такими аргументами — верните результат из кеша."
            ),
            "template": "function memoize(fn) {\n  // Верните кешированную функцию\n}\n",
        },
        {
            "id": "med-4",
            "title": "Глубокое копирование объекта",
            "description": (
                "Напишите функцию deepClone(obj), которая выполняет глубокое копирование объекта "
                "любой вложенности без использования structuredClone или сторонних библиотек."
            ),
            "template": "function deepClone(obj) {\n  // Клонируйте вручную\n}\n",
        },
        {
            "id": "med-5",
            "title": "Удаление falsy-значений",
            "description": (
                "Создайте функцию cleanArray(arr), которая удаляет все falsy значения "
                "(false, 0, '', null, undefined, NaN)."
            ),
            "template": "function cleanArray(arr) {\n  // Отфильтруйте falsy значения\n}\n",
        },
        {
            "id": "med-6",
            "title": "Форматирование строки в camelCase",
            "description": (
                "Реализуйте функцию camelCase(str), которая преобразует строку вида "
                "'hello world example' в 'helloWorldExample'."
            ),
            "template": "function camelCase(str) {\n  // Преобразуйте строку в camelCase\n}\n",
        },
        {
            "id": "med-7",
            "title": "Плоский массив",
            "description": "Создайте функцию flatten(arr), которая превращает вложенный массив в плоский.",
            "template": "function flatten(arr) {\n  // Разверните вложенные массивы\n}\n",
        },
        {
            "id": "med-8",
            "title": "Перевод числа в римские цифры",
            "description": (
                "Реализуйте функцию toRoman(num), преобразующую положительное целое число "
                "в римскую запись (I, V, X, L, C, D, M)."
            ),
            "template": "function toRoman(num) {\n  // Преобразуйте число в римскую нотацию\n}\n",
        },
        {
            "id": "med-9",
            "title": "Фильтрация по диапазону",
            "description": (
                "Реализуйте filterRange(arr, min, max), возвращающую элементы между min и max (включительно). "
                "Результат — новый массив."
            ),
            "template": "function filterRange(arr, min, max) {\n  // Верните элементы диапазона\n}\n",
        },
        {
            "id": "med-10",
            "title": "Анализ строки (частоты символов)",
            "description": (
                "Напишите функцию charFrequency(str), возвращающую объект частот символов строки. "
                "Учитывайте регистр символов."
            ),
            "template": "function charFrequency(str) {\n  // Частоты символов\n}\n",
        },
    ],

    # HARD — паттерны, продвинутые структуры и алгоритмы
    "hard": [
        {
            "id": "hard-1",
            "title": "Throttle function",
            "description": (
                "Реализуйте функцию throttle(fn, delay), которая ограничивает вызов функции fn "
                "не чаще, чем раз в delay миллисекунд."
            ),
            "template": "function throttle(fn, delay) {\n  // Реализуйте throttle\n}\n",
        },
        {
            "id": "hard-2",
            "title": "EventEmitter",
            "description": (
                "Реализуйте класс EventEmitter, поддерживающий методы:\n"
                "on(event, handler), off(event, handler), emit(event, ...args)."
            ),
            "template": (
                "class EventEmitter {\n"
                "  constructor() {\n"
                "    this.events = {};\n"
                "  }\n"
                "  on(event, handler) {}\n"
                "  off(event, handler) {}\n"
                "  emit(event, ...args) {}\n"
                "}\n"
            ),
        },
        {
            "id": "hard-3",
            "title": "Deep Equal",
            "description": (
                "Реализуйте функцию deepEqual(a, b), которая сравнивает два значения "
                "любой вложенности на полное структурное равенство."
            ),
            "template": "function deepEqual(a, b) {\n  // Реализуйте глубокое сравнение\n}\n",
        },
        {
            "id": "hard-4",
            "title": "Свой Promise",
            "description": "Реализуйте класс MyPromise с методами then, catch, finally.",
            "template": (
                "class MyPromise {\n"
                "  constructor(executor) {}\n"
                "  then(onFulfilled, onRejected) {}\n"
                "  catch(onRejected) {}\n"
                "  finally(onFinally) {}\n"
                "}\n"
            ),
        },
        {
            "id": "hard-5",
            "title": "LRU Cache",
            "description": "Реализуйте структуру данных LRUCache с методами get(key) и put(key, value).",
            "template": (
                "class LRUCache {\n"
                "  constructor(capacity) {}\n"
                "  get(key) {}\n"
                "  put(key, value) {}\n"
                "}\n"
            ),
        },
        {
            "id": "hard-6",
            "title": "Шифрование Цезаря",
            "description": (
                "Реализуйте функцию caesarCipher(str, shift), которая шифрует строку "
                "сдвигом букв по алфавиту. Сохраните регистр."
            ),
            "template": "function caesarCipher(str, shift) {\n  // Реализуйте алгоритм\n}\n",
        },
        {
            "id": "hard-7",
            "title": "Мини-база данных в памяти",
            "description": (
                "Реализуйте класс MiniDB, поддерживающий методы insert(obj), find(query), "
                "update(query, patch), delete(query)."
            ),
            "template": (
                "class MiniDB {\n"
                "  constructor() {\n"
                "    this.data = [];\n"
                "  }\n"
                "  insert(obj) {}\n"
                "  find(query) {}\n"
                "  update(query, patch) {}\n"
                "  delete(query) {}\n"
                "}\n"
            ),
        },
        {
            "id": "hard-8",
            "title": "Планировщик задач",
            "description": (
                "Реализуйте функцию scheduler(tasks), где tasks — массив функций, "
                "и каждая функция должна выполняться строго после завершения предыдущей "
                "(поддержка async-функций)."
            ),
            "template": "function scheduler(tasks) {\n  // Запускайте функции последовательно\n}\n",
        },
        {
            "id": "hard-9",
            "title": "Parser mini-JS выражений",
            "description": (
                "Реализуйте функцию parseExpression(expr), которая принимает строку вида "
                "'2 + 3 * (4 - 1)' и вычисляет результат. Требуется реализовать парсер "
                "с поддержкой скобок и приоритетов операций."
            ),
            "template": "function parseExpression(expr) {\n  // Реализуйте парсер выражений\n}\n",
        },
        {
            "id": "hard-10",
            "title": "Своя реализация Redux Store",
            "description": (
                "Реализуйте createStore(reducer), возвращающую объект с методами "
                "getState(), dispatch(action), subscribe(listener)."
            ),
            "template": "function createStore(reducer) {\n  // Реализуйте Redux-подобный store\n}\n",
        },
    ],
}

TASK_BANK_PY = {
    "easy": [
        {
            "id": "py-easy-1",
            "title": "Сложение чисел",
            "description": "Напишите функцию add(a, b), возвращающую сумму.",
            "template": "def add(a, b):\n    pass\n\nprint(add(1, 2))"
        }
    ],
    "medium": [
        {
            "id": "py-med-1",
            "title": "Фибоначчи",
            "description": "Реализуйте рекурсивную или итеративную функцию fib(n).",
            "template": "def fib(n):\n    pass\n\nprint(fib(10))"
        }
    ],
    "hard": [
        {
            "id": "py-hard-1",
            "title": "LRU Cache",
            "description": "Реализуйте класс LRUCache.",
            "template": "class LRUCache:\n    pass"
        }
    ],
}



# -------------------------------------------------
# ХРАНИЛИЩЕ ИНТЕРВЬЮ (пока одна сессия default)
# -------------------------------------------------
interviews: Dict[str, Dict[str, Any]] = {
    "default": {
        "track": None,
        "taskNumber": 0,
        "messages": [],
        "history": [],   # все попытки (компиляции) по ходу интервью
        "results": [],   # результаты по задачам после анализа LLM
        "currentTask": None,
        "waitingCommunication": False,
        "lastCommunicationQuestion": None,
        "pendingResult": None,
        "communications": [],
        "antiCheat": {  # данные античита
            "events": [],  # все события (вставки, выходы из вкладки)
            "codeSnapshots": [],  # снимки кода для анализа
            "analyses": [],  # результаты анализа LLM
            "statistics": {
                "total_paste_count": 0,
                "total_tab_switch_count": 0,
                "total_analyses": 0
            }
        }
    }
}


# -------------------------------------------------
# Функция для починки кривой кодировки stdout/stderr
# -------------------------------------------------
def fix_encoding(text: str | None) -> str | None:
    if text is None:
        return None
    # уже окей – возвращаем как есть
    try:
        text.encode("utf-8")
        return text
    except Exception:
        pass

    # типичная каша UTF-8 → cp1251/latin1
    for enc in ("latin1", "cp1251"):
        try:
            return text.encode(enc).decode("utf-8")
        except Exception:
            continue
    return text

# -------------------------------------------------
# /api/select_track — выбор направления (js/python)
# -------------------------------------------------
@app.post("/api/select_track")
async def select_track(data: dict):
    track = data.get("track")  # "js" / "python"

    session = interviews["default"]
    session["track"] = track
    session["taskNumber"] = 0
    session["messages"] = []
    session["history"] = []
    session["results"] = []
    session["antiCheat"] = {
        "events": [],
        "codeSnapshots": [],
        "analyses": [],
        "statistics": {
            "total_paste_count": 0,
            "total_tab_switch_count": 0,
            "total_analyses": 0
        }
    }

    session["messages"].append({
        "role": "assistant",
        "content": "Вы выбрали направление: " +
                   ("JavaScript" if track == "js" else "Python")
    })

    return {"ok": True}

# -------------------------------------------------
# /api/start_interview — старт сессии
# -------------------------------------------------
@app.post("/api/start_interview")
async def start_interview():
    session = interviews["default"]
    track = session["track"]

    if track == "js":
        bank = TASK_BANK_JS
    else:
        bank = TASK_BANK_PY

    session["taskNumber"] = 1
    session["messages"] = []
    session["history"] = []
    session["results"] = []
    # Античит уже инициализирован в select_track, но на всякий случай проверяем
    if "antiCheat" not in session:
        session["antiCheat"] = {
            "events": [],
            "codeSnapshots": [],
            "analyses": [],
            "statistics": {
                "total_paste_count": 0,
                "total_tab_switch_count": 0,
                "total_analyses": 0
            }
        }

    # выдаём лёгкое задание
    task = random.choice(bank["easy"])
    session["currentTask"] = task
    task["language"] = session["track"]

    session["messages"].append({
        "role": "assistant",
        "content": "Привет! Начинаем техническое интервью. Тебя ждёт 3 задачи.",
    })
    session["messages"].append({
        "role": "assistant",
        "content": f"Задание №1:\n{task['description']}",
    })

    return {
        "messages": session["messages"],
        "task": task,
    }


# -------------------------------------------------
# /api/compile — запуск решения в песочнице
# -------------------------------------------------
@app.post("/api/compile")
async def compile_code(req: CompileRequest):
    session = interviews["default"]

    lang = (req.language or "").lower()

    # определяем раннер
    if lang in ("javascript", "js"):
        sandbox_runner = run_js
    elif lang in ("python", "py"):
        sandbox_runner = run_py
    else:
        return {"error": "Unsupported language"}

    # запускаем код
    result = sandbox_runner(req.code)

    # чиним кривые кодировки
    raw_stdout = result.get("stdout")
    raw_stderr = result.get("stderr")
    stdout = fix_encoding(raw_stdout)
    stderr = fix_encoding(raw_stderr)

    result["stdout"] = stdout
    result["stderr"] = stderr

    # сохраняем историю попыток
    session["history"].append({
        "taskId": req.taskId,
        "attempt": len(session["history"]) + 1,
        "code": req.code,
        "stdout": stdout,
        "stderr": stderr,
        "metrics": result.get("metrics", {}),
    })

    return result


# -------------------------------------------------
# /api/submit — кандидат нажал "Готово"
# -------------------------------------------------
@app.post("/api/submit")
async def submit(req: AssessRequest):
    session = interviews["default"]
    track = session["track"]
    bank = TASK_BANK_JS if track == "js" else TASK_BANK_PY

    task = session.get("currentTask")
    if not task:
        return {
            "messages": [{
                "role": "assistant",
                "content": "Сессия не инициализирована. Обновите страницу."
            }],
            "finished": True
        }

    # анализ кода LLM
    llm_result = analyze_code(
        task_description=task["description"],
        code=req.code,
        run_result=req.runResult,
        final=True,
    )

    # гарантируем наличие ключей
    score_code = llm_result.get("score") or llm_result.get("final_score") or 0
    comment_code = llm_result.get("comment") or "Комментарий отсутствует."

    # сохраняем pendingResult
    session["pendingResult"] = {
        "taskId": task["id"],
        "title": task["title"],
        "description": task["description"],
        "code": req.code,
        "analysis_code": {
            "score": score_code,
            "comment": comment_code
        }
    }

    # сообщение в чат
    session["messages"].append({
        "role": "assistant",
        "content": (
            f"Разбор решения по задаче {task['id']} ({task['title']}):\n"
            f"Оценка за код: {score_code}/100\n"
            f"{comment_code}"
        )
    })

    # задаём вопрос по коммуникации
    comm_question = random.choice([
        "Поясни, почему ты выбрал именно такой подход?",
        "Можешь кратко описать логику своего решения?",
        "Какие альтернативные способы решения возможны?",
        "Как бы ты улучшил алгоритм?",
        "Что является слабым местом твоего решения?"
    ])

    session["waitingCommunication"] = True
    session["lastCommunicationQuestion"] = comm_question

    session["communications"].append({
        "taskId": task["id"],
        "question": comm_question,
        "answer": None,
        "score_comm": None,
        "comment_comm": None
})


    session["messages"].append({
        "role": "assistant",
        "content": (
            "Теперь небольшой вопрос по вашему решению:\n"
            f"{comm_question}"
        )
    })

    return {
        "messages": session["messages"],
        "ask_communication": True,
        "communication_question": comm_question,
        "finished": False,
        "score_code": score_code,
        "comment_code": comment_code,
    }



# -------------------------------------------------
# /api/communication_answer - оценка ответа на вопрос
# -------------------------------------------------
@app.post("/api/communication_answer")
async def communication_answer(data: dict):
    session = interviews["default"]

    if not session.get("waitingCommunication"):
        return {
            "messages": [{
                "role": "assistant",
                "content": "Не жду ответа. Возможно, уже перешли к следующему этапу."
            }],
            "finished": False
        }

    answer = data.get("answer", "").strip()
    # ищем последнюю запись без ответа
    comm_entry = next(
        (c for c in session["communications"] if c["answer"] is None),
        None
    )

    if not comm_entry:
        return {
            "messages": session["messages"],
            "finished": False,
            "error": "Нет активного вопроса для ответа."
        }

    comm_entry["answer"] = answer


    # выключаем режим ожидания ответа
    session["waitingCommunication"] = False


    # LLM анализирует ответ
    llm_comm = analyze_code(
        task_description="Оцени ответ кандидата на уточняющий вопрос.",
        code=answer,
        run_result=None,
        final=True
    )

    comm_score = llm_comm.get("score", 0)
    comm_comment = llm_comm.get("comment", "")

    comm_entry["score_comm"] = comm_score
    comm_entry["comment_comm"] = comm_comment


    # показываем ответ в чате
    session["messages"].append({
        "role": "assistant",
        "content": (
            f"Разбор ответа:\n"
            f"Оценка коммуникации: {comm_score}/100\n"
            f"{comm_comment}"
        )
    })

    # Достаём результаты предыдущего анализа кода
    pending = session["pendingResult"]
    score_code = pending["analysis_code"]["score"]
    comment_code = pending["analysis_code"]["comment"]

    # считаем итоговую оценку задачи
    final_score = round(score_code * 0.7 + comm_score * 0.3, 2)

    final_comment = (
        f"Итоговая оценка за задачу: {final_score}/100\n\n"
        f"Оценка кода: {score_code}/100\n{comment_code}\n\n"
        f"Оценка коммуникации: {comm_score}/100\n{comm_comment}"
    )

    # записываем результат
    session["results"].append({
        "taskId": pending["taskId"],
        "title": pending["title"],
        "description": pending["description"],
        "code": pending["code"],
        "analysis": {
            "score": final_score,
            "comment": final_comment,
            "issues": []
        }
    })


    session["pendingResult"] = None

    # переход к следующей задаче
    track = session["track"]
    bank = TASK_BANK_JS if track == "js" else TASK_BANK_PY

    # ещё не конец
    if session["taskNumber"] < 3:
        session["taskNumber"] += 1

        next_level = "medium" if session["taskNumber"] == 2 else "hard"
        next_task = random.choice(bank[next_level])
        next_task["language"] = track
        session["currentTask"] = next_task

        session["messages"].append({
            "role": "assistant",
            "content": (
                final_comment +
                f"\n\nТеперь задание №{session['taskNumber']}:\n"
                f"{next_task['description']}"
            )
        })

        return {
            "messages": session["messages"],
            "task": next_task,
            "finished": False
        }

    # конец интервью
    final_summary = build_final_summary(session["results"])

    session["messages"].append({
        "role": "assistant",
        "content": final_comment + "\n\n" + "Итог интервью:\n" + final_summary
    })

    pdf_path = generate_report(
        candidate_name="Candidate_1",
        results=session["results"],
        history=session["history"],
        final_summary=final_summary,
        track=session["track"],
        communications=session["communications"],
        anti_cheat_data=session["antiCheat"]
    )

    return {
        "messages": session["messages"],
        "report": pdf_path,
        "finished": True
    }


# -------------------------------------------------
# /api/messages — получить текущий чат (debug)
# -------------------------------------------------
@app.get("/api/messages")
async def get_messages():
    return interviews["default"]["messages"]


# -------------------------------------------------
# /api/anti_cheat_event — обработка события античита
# -------------------------------------------------
@app.post("/api/anti_cheat_event")
async def anti_cheat_event(req: AntiCheatEvent):
    session = interviews["default"]
    anti_cheat = session["antiCheat"]
    
    print(f"[Античит] Получено событие: {req.eventType} для задачи {req.taskId} в {req.timestamp}")
    
    # Сохраняем событие
    event_data = {
        "eventType": req.eventType,
        "timestamp": req.timestamp,
        "taskId": req.taskId,
    }
    anti_cheat["events"].append(event_data)
    
    # Обновляем статистику
    if req.eventType == "paste":
        anti_cheat["statistics"]["total_paste_count"] += 1
        print(f"[Античит] Общее количество вставок: {anti_cheat['statistics']['total_paste_count']}")
    elif req.eventType in ("tab_switch", "window_blur"):
        anti_cheat["statistics"]["total_tab_switch_count"] += 1
        print(f"[Античит] Общее количество выходов из вкладки: {anti_cheat['statistics']['total_tab_switch_count']}")
    
    print(f"[Античит] Событие сохранено. Всего событий: {len(anti_cheat['events'])}")
    return {"ok": True}


# -------------------------------------------------
# /api/anti_cheat_analyze — анализ кода на списывание
# -------------------------------------------------
@app.post("/api/anti_cheat_analyze")
async def anti_cheat_analyze(req: AntiCheatAnalyze):
    session = interviews["default"]
    anti_cheat = session["antiCheat"]
    
    print(f"[Античит] Начало анализа кода для задачи {req.taskId}")
    print(f"[Античит] Длина кода: {req.codeLength} символов")
    
    # Сохраняем снимок кода
    snapshot = {
        "timestamp": req.timestamp,
        "code": req.code,
        "codeLength": req.codeLength,
        "taskId": req.taskId,
    }
    anti_cheat["codeSnapshots"].append(snapshot)
    print(f"[Античит] Снимок кода сохранен. Всего снимков: {len(anti_cheat['codeSnapshots'])}")
    
    # Получаем статистику событий для текущей задачи
    task_events = [e for e in anti_cheat["events"] if e.get("taskId") == req.taskId]
    paste_count = len([e for e in task_events if e.get("eventType") == "paste"])
    tab_switch_count = len([e for e in task_events if e.get("eventType") in ("tab_switch", "window_blur")])
    
    print(f"[Античит] Статистика для задачи {req.taskId}:")
    print(f"  - Вставок из буфера: {paste_count}")
    print(f"  - Выходов из вкладки: {tab_switch_count}")
    
    # Получаем снимки кода для текущей задачи
    task_snapshots = [s for s in anti_cheat["codeSnapshots"] if s.get("taskId") == req.taskId]
    print(f"  - Снимков кода: {len(task_snapshots)}")
    
    # Анализируем через LLM
    print(f"[Античит] Отправка запроса в LLM для анализа...")
    analysis_result = analyze_anti_cheat(
        task_description=req.taskDescription,
        code=req.code,
        paste_count=paste_count,
        tab_switch_count=tab_switch_count,
        code_snapshots=task_snapshots
    )
    
    print(f"[Античит] Результат анализа LLM:")
    print(f"  - Вероятность списывания: {analysis_result.get('cheating_probability', 'N/A')}%")
    print(f"  - Уровень риска: {analysis_result.get('risk_level', 'N/A')}")
    print(f"  - Подозрительных событий: {len(analysis_result.get('suspicious_events', []))}")
    
    # Сохраняем результат анализа
    analysis_data = {
        "timestamp": req.timestamp,
        "taskId": req.taskId,
        "analysis": analysis_result,
    }
    anti_cheat["analyses"].append(analysis_data)
    anti_cheat["statistics"]["total_analyses"] += 1
    print(f"[Античит] Анализ сохранен. Всего анализов: {anti_cheat['statistics']['total_analyses']}")
    
    return {"ok": True, "analysis": analysis_result}


# -------------------------------------------------
# Вспомогательная функция: финальное резюме
# -------------------------------------------------
def build_final_summary(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "Результаты отсутствуют."

    scores = []
    strengths: List[str] = []
    weaknesses: List[str] = []

    for r in results:
        analysis = r.get("analysis", {})
        score = analysis.get("score")
        comment = (analysis.get("comment") or "").lower()
        issues = analysis.get("issues", [])

        if isinstance(score, (int, float)):
            scores.append(score)

        # эвристики по сильным/слабым сторонам
        if "оптимизац" in comment or "эффективн" in comment:
            strengths.append("Хорошая оптимизация и эффективность решений")
        if "читаем" in comment or "чистый код" in comment:
            strengths.append("Хорошая читаемость и структура кода")

        if "не проходит" in comment or "ошибка" in comment or "bug" in comment:
            weaknesses.append("Проблемы с корректностью/устойчивостью кода")
        if "медленно" in comment or "performance" in comment:
            weaknesses.append("Недостаточная производительность решения")

        for issue in issues:
            issue_type = (issue.get("type") or "").lower()
            detail = issue.get("detail") or ""
            if "performance" in issue_type:
                weaknesses.append("Проблемы с производительностью")
            if "readability" in issue_type:
                weaknesses.append("Проблемы с читаемостью кода")
            if "correctness" in issue_type:
                weaknesses.append("Проблемы с корректностью решения")

    avg_score = round(sum(scores) / len(scores), 2) if scores else "N/A"
    strengths_text = ", ".join(sorted(set(strengths))) or "не выявлены"
    weaknesses_text = ", ".join(sorted(set(weaknesses))) or "не выявлены"

    return (
        f"Средняя оценка: {avg_score}/100.\n"
        f"Сильные стороны: {strengths_text}.\n"
        f"Слабые стороны: {weaknesses_text}.\n"
        f"Рекомендации: развивать алгоритмическое мышление, покрывать код тестами "
        f"и уделять больше внимания структуре и читаемости решений."
    )
