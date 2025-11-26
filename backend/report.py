# backend/report.py — красивый PDF-отчёт в стиле HR-Tech

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import uuid
import os
from typing import List, Dict, Any

# Регистрация шрифтов (Roboto с поддержкой кириллицы)
pdfmetrics.registerFont(TTFont("Roboto", "fonts/Roboto-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Roboto-Bold", "fonts/Roboto-Bold.ttf"))


def wrap_text(text: str, width: int = 90) -> list[str]:
    if text is None:
        return []
    return textwrap.wrap(text, width)


def draw_title(c: canvas.Canvas, text: str, y: float) -> float:
    c.setFont("Roboto-Bold", 18)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(40, y, text)
    return y - 30


def draw_subtitle(c: canvas.Canvas, text: str, y: float) -> float:
    c.setFont("Roboto-Bold", 13)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(40, y, text)
    return y - 22


def draw_paragraph(c: canvas.Canvas, text: str, y: float) -> float:
    if not text:
        return y - 10

    c.setFont("Roboto", 10)
    c.setFillColor(colors.black)

    lines = wrap_text(text)
    for line in lines:
        c.drawString(40, y, line)
        y -= 14
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Roboto", 10)

    return y - 10


def draw_code_block(c: canvas.Canvas, text: str, y: float) -> float:
    if not text:
        return y - 10

    c.setFont("Roboto", 9)
    c.setFillColor(colors.HexColor("#1a1a1a"))

    lines = text.split("\n")
    for line in lines:
        wrapped = textwrap.wrap(line, 100)
        for subline in wrapped:
            c.drawString(40, y, subline)
            y -= 12
            if y < 60:
                c.showPage()
                y = 750
                c.setFont("Roboto", 9)

    return y - 10


def generate_report(
    candidate_name: str,
    results: List[Dict[str, Any]],
    history: List[Dict[str, Any]],
    final_summary: str,
    track: str,
    communications: List[Dict[str, Any]],
    anti_cheat_data: Dict[str, Any],   # <-- ДОБАВЛЕНО!!!
) -> str:

    os.makedirs("reports", exist_ok=True)

    filename = f"reports/report_{candidate_name}_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)

    y = 760

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------
    y = draw_title(c, "Отчёт технического интервью", y)

    c.setFont("Roboto", 11)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(40, y, f"Кандидат: {candidate_name}")
    y -= 18

    lang_label = "JavaScript" if track == "js" else "Python"
    c.drawString(40, y, f"Задач в сессии: {len(results)} ({lang_label})")
    y -= 25

    # ---------------------------------------------------------
    # 1. История попыток
    # ---------------------------------------------------------
    y = draw_subtitle(c, "1. История выполнения задач", y)

    if not history:
        y = draw_paragraph(c, "История попыток отсутствует.", y)
    else:
        for h in history:
            c.setFont("Roboto-Bold", 11)
            c.drawString(40, y, f"Попытка #{h.get('attempt')}")
            y -= 16

            metrics = h.get("metrics") or {}
            time_ms = metrics.get("exec_time_ms", "N/A")

            rows = [
                f"Задача: {h.get('taskId')}",
                f"Время выполнения: {time_ms} ms",
                f"stdout: {h.get('stdout')}",
                f"stderr: {h.get('stderr')}",
            ]

            for r in rows:
                y = draw_paragraph(c, r, y)

            y -= 6
            if y < 80:
                c.showPage()
                y = 760

    # ---------------------------------------------------------
    # 2. Решения кандидата
    # ---------------------------------------------------------
    y = draw_subtitle(c, "2. Решения кандидата по задачам", y)

    for r in results:
        y = draw_paragraph(c, f"Задача {r['taskId']} — {r['title']}", y)
        y = draw_paragraph(c, r["description"], y)
        y = draw_code_block(c, r["code"], y)

        y -= 6
        if y < 80:
            c.showPage()
            y = 760

    # ---------------------------------------------------------
    # 3. Анализ решений (LLM)
    # ---------------------------------------------------------
    y = draw_subtitle(c, "3. Анализ решений по задачам (LLM)", y)

    for r in results:
        analysis = r["analysis"]
        score = analysis.get("score", "N/A")
        comment = analysis.get("comment", "")
        issues = analysis.get("issues", [])

        y = draw_paragraph(c, f"Задача {r['taskId']} — оценка: {score}/100", y)
        y = draw_paragraph(c, f"Комментарий: {comment}", y)

        if issues:
            for issue in issues:
                y = draw_paragraph(
                    c,
                    f"- {issue.get('type')}: {issue.get('detail')}",
                    y,
                )
        else:
            y = draw_paragraph(c, "Замечаний не зафиксировано.", y)

        y -= 6
        if y < 80:
            c.showPage()
            y = 760

    # ---------------------------------------------------------
    # 4. Итоговая оценка
    # ---------------------------------------------------------
    y = draw_subtitle(c, "4. Итоговая оценка кандидата", y)
    y = draw_paragraph(c, final_summary, y)

    # ---------------------------------------------------------
    # 5. Коммуникативные ответы кандидата
    # ---------------------------------------------------------
    y = draw_subtitle(c, "5. Коммуникативные ответы кандидата", y)

    if not communications:
        y = draw_paragraph(c, "Коммуникативных вопросов не было.", y)
    else:
        for entry in communications:
            y = draw_paragraph(c, f"Задача: {entry['taskId']}", y)
            y = draw_paragraph(c, f"Вопрос: {entry['question']}", y)
            y = draw_paragraph(c, f"Ответ кандидата: {entry['answer']}", y)
            y = draw_paragraph(
                c,
                f"Оценка коммуникации: {entry.get('score_comm')}/100",
                y,
            )
            y = draw_paragraph(c, f"{entry.get('comment_comm')}", y)

            y -= 8
            if y < 80:
                c.showPage()
                y = 760

    # ---------------------------------------------------------
    # 6. Анализ античита
    # ---------------------------------------------------------
    y = draw_subtitle(c, "6. Анализ античита", y)
    
    stats = anti_cheat_data.get("statistics", {})
    total_paste = stats.get("total_paste_count", 0)
    total_tab_switch = stats.get("total_tab_switch_count", 0)
    total_analyses = stats.get("total_analyses", 0)
    
    y = draw_paragraph(
        c,
        f"Общая статистика: вставок из буфера - {total_paste}, выходов из вкладки - {total_tab_switch}, анализов кода - {total_analyses}",
        y
    )
    
    analyses = anti_cheat_data.get("analyses", [])
    if analyses:
        # Группируем по задачам
        task_analyses: Dict[str, List[Dict[str, Any]]] = {}
        for analysis in analyses:
            task_id = analysis.get("taskId", "unknown")
            if task_id not in task_analyses:
                task_analyses[task_id] = []
            task_analyses[task_id].append(analysis)
        
        for task_id, task_analysis_list in task_analyses.items():
            # Берем последний анализ для каждой задачи
            last_analysis = task_analysis_list[-1]
            analysis_result = last_analysis.get("analysis", {})
            
            cheating_prob = analysis_result.get("cheating_probability", 0)
            risk_level = analysis_result.get("risk_level", "low")
            comment = analysis_result.get("comment", "")
            suspicious_events = analysis_result.get("suspicious_events", [])
            
            y = draw_paragraph(c, f"Задача: {task_id}", y)
            y = draw_paragraph(
                c,
                f"Вероятность списывания: {cheating_prob}% (уровень риска: {risk_level})",
                y
            )
            
            if comment:
                y = draw_paragraph(c, f"Комментарий: {comment}", y)
            
            if suspicious_events:
                y = draw_paragraph(c, "Подозрительные события:", y)
                for event in suspicious_events:
                    event_type = event.get("type", "")
                    event_desc = event.get("description", "")
                    event_severity = event.get("severity", "")
                    y = draw_paragraph(
                        c,
                        f"  - {event_type} ({event_severity}): {event_desc}",
                        y
                    )
            
            y -= 8
            if y < 80:
                c.showPage()
                y = 760
    else:
        y = draw_paragraph(c, "Анализы античита отсутствуют.", y)
    
    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------
    c.setFont("Roboto", 9)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(
        40,
        30,
        "Отчёт сгенерирован автоматически AI HR Interview System powered by FOTUR",
    )

    c.save()
    return filename
