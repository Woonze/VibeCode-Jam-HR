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
    """Перенос строк для длинных текстов."""
    if text is None:
        return []
    return textwrap.wrap(text, width)


def draw_title(c: canvas.Canvas, text: str, y: float) -> float:
    """Большой заголовок страницы."""
    c.setFont("Roboto-Bold", 18)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(40, y, text)
    return y - 30


def draw_subtitle(c: canvas.Canvas, text: str, y: float) -> float:
    """Подзаголовок раздела."""
    c.setFont("Roboto-Bold", 13)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(40, y, text)
    return y - 22


def draw_paragraph(c: canvas.Canvas, text: str, y: float) -> float:
    """Базовый абзац с переносом строк."""
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
    """Code block для кода кандидата."""
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
) -> str:
    """
    Создание красивого PDF-отчёта по интервью.

    results: список задач:
      {
        "taskId": str,
        "title": str,
        "description": str,
        "code": str,
        "analysis": {
            "score": int,
            "comment": str,
            "issues": [{type, detail}, ...]
        }
      }

    history: список попыток запуска кода (из /api/compile)
    """

    os.makedirs("reports", exist_ok=True)

    filename = f"reports/report_{candidate_name}_{uuid.uuid4().hex}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter  # noqa: F841 (на будущее)

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
            c.setFillColor(colors.HexColor("#222222"))
            c.drawString(40, y, f"Попытка #{h.get('attempt')}")
            y -= 16

            c.setFont("Roboto", 10)
            c.setFillColor(colors.black)

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
    # 2. Решения кандидата по задачам
    # ---------------------------------------------------------
    y = draw_subtitle(c, "2. Решения кандидата по задачам", y)

    if not results:
        y = draw_paragraph(c, "Решения кандидата отсутствуют.", y)
    else:
        for r in results:
            task_header = f"Задача {r.get('taskId')} — {r.get('title')}"
            y = draw_paragraph(c, task_header, y)
            y = draw_paragraph(c, r.get("description", ""), y)
            y = draw_code_block(c, r.get("code", ""), y)
            y -= 6
            if y < 80:
                c.showPage()
                y = 760

    # ---------------------------------------------------------
    # 3. Анализ по задачам (LLM)
    # ---------------------------------------------------------
    y = draw_subtitle(c, "3. Анализ решений по задачам (LLM)", y)

    if not results:
        y = draw_paragraph(c, "Анализ отсутствует.", y)
    else:
        for r in results:
            analysis = r.get("analysis") or {}
            score = analysis.get("score", "N/A")
            comment = analysis.get("comment", "")
            issues = analysis.get("issues", [])

            header = f"Задача {r.get('taskId')} — оценка: {score}/100"
            y = draw_paragraph(c, header, y)
            y = draw_paragraph(c, f"Комментарий: {comment}", y)

            if issues:
                y = draw_paragraph(c, "Ключевые замечания:", y)
                for issue in issues:
                    issue_text = f"- {issue.get('type', '')}: {issue.get('detail', '')}"
                    y = draw_paragraph(c, issue_text, y)
            else:
                y = draw_paragraph(c, "Замечаний для этой задачи не зафиксировано.", y)

            y -= 6
            if y < 80:
                c.showPage()
                y = 760

    # ---------------------------------------------------------
    # 4. Итоговая оценка кандидата
    # ---------------------------------------------------------
    y = draw_subtitle(c, "4. Итоговая оценка кандидата", y)
    y = draw_paragraph(c, final_summary, y)

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
