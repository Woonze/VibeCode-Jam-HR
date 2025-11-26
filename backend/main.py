# backend/main.py основной файл с эндпоинтами FastAPI
import random
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import CompileRequest, AssessRequest  # CompileResponse/AssessResponse можно не использовать жёстко
from sandbox import run_js, run_py
from llm_client import analyze_code
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

    lang = req.language

    if lang == "javascript":
        return run_js(req.code)

    elif lang == "python":
        return run_py(req.code)

    else:
        return {"error": "Unsupported language"}

    # запускаем код в песочнице
    run = run_js if session["track"] == "js" else run_py
    result = run(req.code)

    # аккуратно чиним кодировку stdout/stderr
    raw_stdout = result.get("stdout")
    raw_stderr = result.get("stderr")
    stdout = fix_encoding(raw_stdout)
    stderr = fix_encoding(raw_stderr)

    # обновляем результат, чтобы фронт сразу получил нормальный русский
    result["stdout"] = stdout
    result["stderr"] = stderr

    # сохраняем попытку
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
        # на всякий случай, если фронт дернул submit без start_interview
        return {
            "messages": [{
                "role": "assistant",
                "content": "Сессия не инициализирована. Обновите страницу для начала интервью.",
            }],
            "finished": True,
        }

    # анализируем решение текущей задачи
    llm_result = analyze_code(
        task_description=task["description"],
        code=req.code,
        run_result=req.runResult,
        final=True,
    )

    score = llm_result.get("score", 0)
    comment = llm_result.get("comment", "")

    # сохраняем результат по задаче
    session["results"].append({
        "taskId": task["id"],
        "title": task["title"],
        "description": task["description"],
        "code": req.code,
        "analysis": llm_result,
    })

    # короткий разбор в чат
    session["messages"].append({
        "role": "assistant",
        "content": (
            f"Разбор решения по задаче {task['id']} ({task['title']}):\n"
            f"Оценка: {score}/100\n"
            f"{comment}"
        ),
    })

    # ----------------------------------------
    # Если ещё не 3-я задача — выдаём следующую
    # ----------------------------------------
    if session["taskNumber"] < 3:
        session["taskNumber"] += 1

        if session["taskNumber"] == 2:
            next_task = random.choice(bank["medium"])
        else:
            next_task = random.choice(bank["hard"])
        
        next_task["language"] = session["track"]

        session["currentTask"] = next_task

        session["messages"].append({
            "role": "assistant",
            "content": (
                f"Теперь задание №{session['taskNumber']}:\n"
                f"{next_task['description']}"
            ),
        })

        return {
            "messages": session["messages"],
            "task": next_task,
            "finished": False,
            "score": score,
            "comment": comment,
        }

    # ----------------------------------------
    # Это была 3-я задача → финальное резюме
    # ----------------------------------------
    final_summary = build_final_summary(session["results"])

    session["messages"].append({
        "role": "assistant",
        "content": f"Итог технического интервью:\n{final_summary}",
    })

    # генерируем красивый PDF
    pdf_path = generate_report(
        candidate_name="Candidate_1",
        results=session["results"],
        history=session["history"],
        final_summary=final_summary,
        track=session["track"]
    )

    return {
        "messages": session["messages"],
        "report": pdf_path,
        "finished": True,
        "score": score,
        "comment": comment,
    }


# -------------------------------------------------
# /api/messages — получить текущий чат (debug)
# -------------------------------------------------
@app.get("/api/messages")
async def get_messages():
    return interviews["default"]["messages"]


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
