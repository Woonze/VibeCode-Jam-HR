# backend/main.py основной файл с эндпоинтами FastAPI
import random
from pydantic import BaseModel
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import CompileRequest, AssessRequest, AntiCheatEvent, AntiCheatAnalyze  # CompileResponse/AssessResponse можно не использовать жёстко
from sandbox import run_js, run_py
from llm_client import client, analyze_code, analyze_communication, analyze_anti_cheat, analyze_soft_skill
from report import generate_report
from tests_runner import run_tests_js, run_tests_py
from TEST_BANK_JS import TEST_BANK_JS
from TEST_BANK_PY import TEST_BANK_PY
from TASK_BANK_PY import TASK_BANK_PY
from TASK_BANK_JS import TASK_BANK_JS
from SOFT_SKILLS_BANK import SOFT_SKILLS_BANK

import json

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
# БАНК ЗАДАНИЙ (вынес в отедльные файлы)
# -------------------------------------------------

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
    session["soft_tasks"] = []
    session["currentSoftIndex"] = 0
    session["soft_results"] = []
    session["soft_stage"] = False
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


    # Запуск тестов
    if track == "js":
        test_results = run_tests_js(task["id"], req.code, TEST_BANK_JS)
    else:
        test_results = run_tests_py(task["id"], req.code, TEST_BANK_PY)

    # считаем балл за тесты (30% от итоговой оценки)
    passed = sum(1 for t in test_results if t["passed"])
    total = len(test_results)
    tests_score = int((passed / total) * 100) if total > 0 else 0


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
        "tests": test_results,
        "tests_score": tests_score,
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
        "Поясните, почему вы выбрали именно такой подход?",
        "Можете кратко описать логику вашего решения?",
        "Какие альтернативные способы решения возможны?",
        "Как бы вы улучшили алгоритм?",
        "Что является слабым местом вашего решения?"
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

        # ----- LLM -----
        "score_code": score_code,
        "comment_code": comment_code,

        # ----- TESTS -----
        "tests": test_results,
        "tests_score": tests_score,
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
    llm_comm = analyze_communication(
    answer=answer,
    question=session.get("lastCommunicationQuestion", ""),
    code=session["pendingResult"]["code"],
    task_description=session["pendingResult"]["description"],
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

    # Техническая часть завершена — запускаем soft-skills
    session["soft_stage"] = True
    session["currentSoftIndex"] = 0
    k = min(3, len(SOFT_SKILLS_BANK))  # на всякий случай, если в банке < 3
    session["soft_tasks"] = random.sample(SOFT_SKILLS_BANK, k)
    session["soft_results"] = []

    soft_task = session["soft_tasks"][0]

    session["messages"].append({
        "role": "assistant",
        "content": (
            final_comment +
            "\n\nТехническая часть интервью завершена!\n"
            "Теперь переходим к soft-skills.\n\n"
            f"Ситуация №1:\n{soft_task['description']}\n\n"
            "Введите ваш ответ ниже."
        )
    })


    return {
        "messages": session["messages"],
        "soft_question": {
            "id": soft_task["id"],
            "description": soft_task["description"],
            "template": soft_task["template"]
        },
        "finished": False
    }


# -------------------------------------------------
# /api/soft_answer — ответ на вопрос soft-skills
# -------------------------------------------------
class SoftAnswer(BaseModel):
    taskId: str
    answer: str
    
@app.post("/api/soft_answer")
async def soft_answer(req: SoftAnswer):
    session = interviews["default"]

    if not session["soft_stage"]:
        return {"error": "Soft-skills stage is not started yet."}

    index = session["currentSoftIndex"]
    tasks = session["soft_tasks"]

    if index >= len(tasks):
        return {"error": "All soft-skills tasks already completed."}

    task = tasks[index]

    llm_result = analyze_soft_skill(
        question=task["description"],
        template=task["template"],
        answer=req.answer
    )

    # сохраняем результат
    session["soft_results"].append({
        "taskId": task["id"],
        "description": task["description"],
        "answer": req.answer,
        "analysis": llm_result
    })

    # готовим следующий вопрос
    session["currentSoftIndex"] += 1

    def format_summary_text(summary: dict) -> str:
        text = []
        text.append(f"Средняя оценка за код: {summary['average_code_score']}/100")
        text.append(f"Средняя оценка за коммуникацию: {summary['average_comm_score']}/100\n")

        text.append("\nРекомендации:")
        for r in summary["recommendations"]:
            text.append(f"- {r}")

        text.append(f"\nИтог:\n{summary['summary']}")

        return "\n".join(text)

    # если были последние
    if session["currentSoftIndex"] >= len(tasks):
        session["soft_stage"] = False

        # Финальный суммарный отчёт с учётом soft-skills
        final_summary = build_final_summary(
            session["results"],
            session["communications"],
            session["soft_results"],
            session["antiCheat"]
        )

        final_summary_text = format_summary_text(final_summary)

        session["messages"].append({
            "role": "assistant",
            "content": (
                "Soft-skills интервью завершено!\n\n"
                "Итог интервью:\n" + final_summary_text
            )
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


    # иначе отправляем следующий вопрос
    next_task = tasks[session["currentSoftIndex"]]

    session["messages"].append({
        "role": "assistant",
        "content": (
            f"Спасибо за ответ!\n\n"
            f"Следующая ситуация:\n{next_task['description']}\n\n"
            "Введите ваш ответ ниже."
        )
    })

    return {
        "messages": session["messages"],
        "soft_finished": False,
        "next_question": {
            "id": next_task["id"],
            "description": next_task["description"],
            "template": next_task["template"]
        }
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
def build_final_summary(
        results: List[Dict[str, Any]], 
        communications: List[Dict[str, Any]], 
        soft_results: List[Dict[str, Any]],
        anti_cheat_data: Dict[str, Any]
) -> dict:
    """
    Финальный агрегированный отчёт по интервью:

    - average_code_score: средний балл за задачи (0–100)
    - average_comm_score: средний балл за коммуникацию по технической части (0–100)
    - soft_scores: агрегаты по soft-skills (по метрикам + общий)
    - anti_cheat: краткая сводка по античиту
    - overall_score: интегральный балл кандидата
    - hire_decision: короткий вердикт ("Рекомендован", "Условно рекомендован", "Не рекомендован")
    - hire_recommendation: человеко-читаемое пояснение
    - strengths / weaknesses / recommendations / summary: текст от LLM
    """

    import json

    # ---------- 1. Средние оценки по коду ----------
    code_scores: list[float] = []
    for r in results:
        s = r.get("analysis", {}).get("score")
        if isinstance(s, (int, float)):
            code_scores.append(s)

    avg_code = round(sum(code_scores) / len(code_scores), 2) if code_scores else 0.0

    # ---------- 2. Средние оценки по коммуникации (тех часть) ----------
    comm_scores: list[float] = []
    for c in communications:
        s = c.get("score_comm")
        if isinstance(s, (int, float)):
            comm_scores.append(s)

    avg_comm = round(sum(comm_scores) / len(comm_scores), 2) if comm_scores else 0.0

    # ---------- 3. Агрегаты по soft-skills ----------
    soft_comm, soft_team, soft_adapt, soft_lead, soft_prob = [], [], [], [], []

    for item in soft_results:
        a = item.get("analysis", {}) or {}
        if isinstance(a.get("score_communication"), (int, float)):
            soft_comm.append(a["score_communication"])
        if isinstance(a.get("score_teamwork"), (int, float)):
            soft_team.append(a["score_teamwork"])
        if isinstance(a.get("score_adaptability"), (int, float)):
            soft_adapt.append(a["score_adaptability"])
        if isinstance(a.get("score_leadership"), (int, float)):
            soft_lead.append(a["score_leadership"])
        if isinstance(a.get("score_problem_solving"), (int, float)):
            soft_prob.append(a["score_problem_solving"])

    def avg(lst: list[float]) -> float:
        return round(sum(lst) / len(lst), 2) if lst else 0.0

    soft_scores = {
        "communication": avg(soft_comm),
        "teamwork": avg(soft_team),
        "adaptability": avg(soft_adapt),
        "leadership": avg(soft_lead),
        "problem_solving": avg(soft_prob),
    }

    # общий soft-skills балл (просто среднее по всем метрикам)
    soft_values = [v for v in soft_scores.values() if isinstance(v, (int, float))]
    soft_overall = round(sum(soft_values) / len(soft_values), 2) if soft_values else 0.0
    soft_scores["overall"] = soft_overall

    # ---------- 4. Античит: сводка ----------
    analyses = anti_cheat_data.get("analyses", []) or []
    stats = anti_cheat_data.get("statistics", {}) or {}

    if analyses:
        last_analysis = analyses[-1].get("analysis", {}) or {}
        cheating_probability = float(last_analysis.get("cheating_probability", 0) or 0)
        risk_level = (last_analysis.get("risk_level") or "low").lower()
    else:
        cheating_probability = 0.0
        risk_level = "low"

    # русифицируем риск
    risk_map = {"low": "низкий", "medium": "средний", "high": "высокий"}
    risk_ru = risk_map.get(risk_level, risk_level)

    anti_cheat_summary = (
        f"Вероятность списывания: {cheating_probability:.0f}%. "
        f"Уровень риска: {risk_ru}."
    )

    if risk_level == "high" or cheating_probability >= 70:
        cheating_flag = "Есть высокие подозрения на списывание."
    elif risk_level == "medium" or cheating_probability >= 40:
        cheating_flag = "Есть отдельные признаки возможного списывания, требуется дополнительная проверка."
    else:
        cheating_flag = "Значимых признаков списывания не выявлено."

    anti_cheat_block = {
        "cheating_probability": cheating_probability,
        "risk_level": risk_level,
        "risk_level_ru": risk_ru,
        "summary": anti_cheat_summary,
        "flag": cheating_flag,
        "statistics": {
            "total_paste_count": stats.get("total_paste_count", 0),
            "total_tab_switch_count": stats.get("total_tab_switch_count", 0),
            "total_analyses": stats.get("total_analyses", 0),
        },
    }

    # ---------- 5. Интегральный балл и решение по найму ----------
    overall_score = round(
        avg_code * 0.5    # основа — технические задачи
        + avg_comm * 0.2  # коммуникация при обсуждении решений
        + soft_overall * 0.3,  # soft-skills
        2,
    )

    if risk_level == "high" or cheating_probability >= 70:
        hire_decision = "Не рекомендован"
        hire_recommendation = (
            "Несмотря на результаты по задачам, высокий риск списывания. "
            "Не рекомендован к найму без дополнительной жесткой проверки."
        )
    else:
        if overall_score >= 80:
            hire_decision = "Рекомендован"
            hire_recommendation = (
                "Кандидат демонстрирует сильный технический уровень и адекватные soft-skills. "
                "Рекомендован к найму."
            )
        elif overall_score >= 60:
            hire_decision = "Условно рекомендован"
            hire_recommendation = (
                "Кандидат показывает приемлемый уровень, но есть зоны роста. "
                "Возможен найм при условии планируемого дообучения/испытательного срока."
            )
        else:
            hire_decision = "Не рекомендован"
            hire_recommendation = (
                "Текущий уровень по сумме метрик ниже ожидаемого. "
                "Не рекомендован к найму на целевую позицию."
            )

    # ---------- 6. Запрашиваем от LLM strengths / weaknesses / recommendations / summary ----------
    prompt = f"""
Ты — старший IT-рекрутер.

Проанализируй результаты технического интервью.

ОЦЕНКИ КОДА:
{json.dumps(results, ensure_ascii=False, indent=2)}

ОЦЕНКИ КОММУНИКАЦИИ:
{json.dumps(communications, ensure_ascii=False, indent=2)}

ОЦЕНКИ SOFT-SKILLS:
{json.dumps(soft_results, ensure_ascii=False, indent=2)}

Сформируй разнообразный, НЕ шаблонный отчёт.

Формат JSON:
{{
  "strengths": [строка...],
  "weaknesses": [строка...],
  "recommendations": [строка...],
  "summary": "короткий итог"
}}
"""

    resp = client.chat.completions.create(
        model="qwen3-32b-awq",
        messages=[
            {"role": "system", "content": "Ты эксперт по техническим интервью, отвечай только JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = resp.choices[0].message.content
    parsed = json.loads(raw)

    # ---------- 7. Склеиваем всё в один dict ----------
    return {
        "average_code_score": avg_code,
        "average_comm_score": avg_comm,
        "soft_results": soft_results,
        "soft_scores": soft_scores,
        "anti_cheat": anti_cheat_block,
        "overall_score": overall_score,
        "hire_decision": hire_decision,
        "hire_recommendation": hire_recommendation,
        **parsed,  # strengths / weaknesses / recommendations / summary
    }