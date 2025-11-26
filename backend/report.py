# backend/report.py — улучшённый визуально PDF отчёт (HR-Tech Premium Style)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import uuid
import os
from typing import List, Dict, Any

# ----------------------------------------------
# Регистрация шрифтов
# ----------------------------------------------
pdfmetrics.registerFont(TTFont("Roboto", "fonts/Roboto-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Roboto-Bold", "fonts/Roboto-Bold.ttf"))

ACCENT = colors.HexColor("#0A84FF")
SUBTLE_BG = colors.HexColor("#F5F7FA")
CODE_BG = colors.HexColor("#ECEFF4")
TEXT = colors.HexColor("#222222")


# ----------------------------------------------
# Утилиты форматирования
# ----------------------------------------------
def wrap_text(text: str, width: int = 95) -> list[str]:
    if not text:
        return []
    return textwrap.wrap(text, width)


def draw_section_header(c, text, y):
    """Большой красивый заголовок секции"""
    c.setFont("Roboto-Bold", 16)
    c.setFillColor(ACCENT)
    c.drawString(40, y, text)
    return y - 26


def draw_subtitle(c, text, y):
    """Подзаголовок внутри секции"""
    c.setFont("Roboto-Bold", 13)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(40, y, text)
    return y - 20


def draw_paragraph(c, text, y, indent=0):
    """Обычный параграф"""
    if not text:
        return y - 10

    c.setFont("Roboto", 10)
    c.setFillColor(TEXT)

    for line in wrap_text(text):
        c.drawString(40 + indent, y, line)
        y -= 14
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Roboto", 10)

    return y - 8


def draw_bullet_list(c, items, y):
    """Красивый список с маркерами"""
    for item in items:
        y = draw_paragraph(c, f"• {item}", y)
    return y


def draw_code_block(c, text, y):
    """Серая подложка + моноширинный код"""
    if not text:
        return y - 10

    # cначала вычисляем все строки с учетом переноса
    all_lines = []
    for line in text.split("\n"):
        # переносим длинные строки
        wrapped = textwrap.wrap(line, 95)
        if wrapped:
            all_lines.extend(wrapped)
        else:
            all_lines.append("")  # пустая строка
    
    # вычисляем высоту блока
    block_height = len(all_lines) * 12 + 8
    
    # проверяем, помещается ли блок на текущей странице
    if y - block_height < 60:
        c.showPage()
        y = 760
    
    # Рисуем фон
    c.setFillColor(CODE_BG)
    c.rect(30, y - 4, 550, -block_height, fill=1, stroke=0)

    # Текст
    c.setFont("Roboto", 9)
    c.setFillColor(colors.black)
    
    start_y = y
    for idx, subline in enumerate(all_lines):
        # Проверяем, нужна ли новая страница
        if y < 60:
            c.showPage()
            y = 760
            # Перерисовываем фон на новой странице
            remaining_lines = all_lines[idx:]
            remaining_height = len(remaining_lines) * 12 + 8
            c.setFillColor(CODE_BG)
            c.rect(30, y - 4, 550, -remaining_height, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.setFont("Roboto", 9)
        
        c.drawString(40, y, subline)
        y -= 12

    return y - 16


def new_page_if_needed(c, y):
    if y < 80:
        c.showPage()
        return 760
    return y


# ----------------------------------------------
# ГЕНЕРАЦИЯ ОТЧЁТА
# ----------------------------------------------
def generate_report(
    candidate_name: str,
    results: List[Dict[str, Any]],
    history: List[Dict[str, Any]],
    final_summary: Dict[str, Any],
    track: str,
    communications: List[Dict[str, Any]],
    anti_cheat_data: Dict[str, Any],
) -> str:

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{candidate_name}_{uuid.uuid4().hex}.pdf"

    c = canvas.Canvas(filename, pagesize=letter)
    y = 760

    # ------------------------------------------------
    # HEADER
    # ------------------------------------------------
    y = draw_section_header(c, "Отчёт технического интервью", y)

    c.setFont("Roboto-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(40, y, f"Кандидат: {candidate_name}")
    y -= 18

    lang_label = "JavaScript" if track == "js" else "Python"
    c.drawString(40, y, f"Направление: {lang_label}")
    y -= 14

    c.drawString(40, y, f"Количество задач: {len(results)}")
    y -= 25

    # ------------------------------------------------
    # 1. History
    # ------------------------------------------------
    y = draw_section_header(c, "1. История выполнения задач", y)

    if not history:
        y = draw_paragraph(c, "История отсутствует.", y)
    else:
        for attempt in history:
            y = draw_subtitle(c, f"Попытка #{attempt['attempt']}", y)

            metrics = attempt.get("metrics", {})
            time_ms = metrics.get("exec_time_ms", "N/A")

            rows = [
                f"Задача: {attempt.get('taskId')}",
                f"Время выполнения: {time_ms} ms",
                f"stdout: {attempt.get('stdout')}",
                f"stderr: {attempt.get('stderr')}",
            ]

            for row in rows:
                y = draw_paragraph(c, row, y)

            y -= 6
            y = new_page_if_needed(c, y)

    # ------------------------------------------------
    # 2. Решения
    # ------------------------------------------------
    y = draw_section_header(c, "2. Решения кандидата", y)

    for r in results:
        y = draw_subtitle(c, f"{r['taskId']} — {r['title']}", y)
        y = draw_paragraph(c, r['description'], y)
        y = draw_code_block(c, r['code'], y)
        y -= 6
        y = new_page_if_needed(c, y)

    # ------------------------------------------------
    # 3. LLM-анализ
    # ------------------------------------------------
    y = draw_section_header(c, "3. Анализ решений (LLM)", y)

    for r in results:
        analysis = r["analysis"]

        y = draw_subtitle(c, f"{r['taskId']} — {analysis.get('score')}/100", y)
        y = draw_paragraph(c, f"Комментарий:", y)
        y = draw_paragraph(c, analysis.get("comment", ""), y, indent=20)

        issues = analysis.get("issues", [])
        if issues:
            y = draw_paragraph(c, "Выявленные проблемы:", y)
            for issue in issues:
                issue_type = issue.get('type', 'unknown')
                issue_detail = issue.get('detail', '')
                y = draw_paragraph(
                    c, f"• [{issue_type}]: {issue_detail}", y, indent=20
                )
        # Если issues пустой, но оценка низкая или есть критика в комментарии - не пишем "проблем не обнаружено"
        elif analysis.get("score", 100) < 70 or ("проблем" in analysis.get("comment", "").lower() or "ошибк" in analysis.get("comment", "").lower()):
            y = draw_paragraph(c, "Детали анализа см. в комментарии выше.", y)

        y -= 8
        y = new_page_if_needed(c, y)

    # ------------------------------------------------
    # 4. Итоговая оценка
    # ------------------------------------------------
    y = draw_section_header(c, "4. Итоговая оценка кандидата", y)

    # карточка итогов
    c.setFillColor(SUBTLE_BG)
    c.rect(30, y - 4, 550, -90, fill=1, stroke=0)
    c.setFillColor(TEXT)

    y -= 14
    y = draw_paragraph(c, f"Средняя оценка за код: {final_summary['average_code_score']}/100", y, indent=10)
    y = draw_paragraph(c, f"Средняя оценка за коммуникацию: {final_summary['average_comm_score']}/100", y, indent=10)
    y -= 8

    y = draw_subtitle(c, "Сильные стороны:", y)
    y = draw_bullet_list(c, final_summary["strengths"], y)

    y = draw_subtitle(c, "Слабые стороны:", y)
    y = draw_bullet_list(c, final_summary["weaknesses"], y)

    y = draw_subtitle(c, "Рекомендации:", y)
    y = draw_bullet_list(c, final_summary["recommendations"], y)

    y = draw_paragraph(c, f"Итог: {final_summary['summary']}", y)

    # ------------------------------------------------
    # 5. Коммуникация
    # ------------------------------------------------
    y = draw_section_header(c, "5. Коммуникативные ответы", y)

    if not communications:
        y = draw_paragraph(c, "Коммуникационных вопросов не было.", y)
    else:
        for entry in communications:
            y = draw_subtitle(c, f"Задача: {entry['taskId']}", y)
            y = draw_paragraph(c, f"Вопрос: {entry['question']}", y)
            y = draw_paragraph(c, f"Ответ: {entry['answer']}", y, indent=10)
            y = draw_paragraph(c, f"Оценка: {entry['score_comm']}/100", y)
            y = draw_paragraph(c, entry["comment_comm"], y, indent=10)

            y -= 10
            y = new_page_if_needed(c, y)

    # ------------------------------------------------
    # 6. Античит
    # ------------------------------------------------
    y = draw_section_header(c, "6. Анализ античита", y)

    stats = anti_cheat_data.get("statistics", {})
    y = draw_paragraph(
        c,
        f"Вставок: {stats.get('total_paste_count')}, "
        f"Смена вкладки: {stats.get('total_tab_switch_count')}, "
        f"Анализов LLM: {stats.get('total_analyses')}",
        y
    )

    analyses = anti_cheat_data.get("analyses", [])

    if analyses:
        tasks = {}
        for a in analyses:
            tasks.setdefault(a["taskId"], []).append(a)

        for task_id, arr in tasks.items():
            last = arr[-1]["analysis"]

            y = draw_subtitle(c, f"Задача: {task_id}", y)
            y = draw_paragraph(
                c,
                f"Вероятность списывания: {last.get('cheating_probability')}% "
                f"(уровень: {last.get('risk_level')})",
                y
            )

            if last.get("comment"):
                y = draw_paragraph(c, last["comment"], y)

            events = last.get("suspicious_events", [])
            if events:
                y = draw_paragraph(c, "Подозрительные события:", y)
                for e in events:
                    y = draw_paragraph(
                        c,
                        f"• {e['type']} ({e['severity']}): {e['description']}",
                        y,
                        indent=20
                    )

            y -= 8
            y = new_page_if_needed(c, y)

    else:
        y = draw_paragraph(c, "Подозрительных признаков не обнаружено.", y)

        # ---------------- 7. Soft-Skills интервью ----------------
    y = draw_subtitle(c, "7. Soft-Skills интервью", y)

    soft_results = final_summary.get("soft_results", [])

    if not soft_results:
        y = draw_paragraph(c, "Soft-skills вопросы не задавались.", y)
    else:
        for entry in soft_results:
            y = draw_paragraph(c, f"Ситуация: {entry['taskId']}", y)
            y = draw_paragraph(c, entry["description"], y)

            # Ответ
            y = draw_paragraph(c, "Ответ кандидата:", y)
            y = draw_paragraph(c, entry["answer"], y)

            analysis = entry["analysis"]

            # Метрики
            y = draw_paragraph(c, "---", y)

            metrics = [
                ("Коммуникация", analysis.get("communication")),
                ("Командная работа", analysis.get("teamwork")),
                ("Адаптивность", analysis.get("adaptability")),
                ("Лидерство", analysis.get("leadership")),
                ("Решение проблем", analysis.get("problem_solving")),
            ]

            for title, value in metrics:
                if value is not None:
                    y = draw_paragraph(
                        c, f"- {title}: {value}/100", y
                    )

            # Итоговая оценка
            final_score = analysis.get("final_score")
            if final_score is not None:
                y = draw_paragraph(
                    c,
                    f"Итоговая оценка soft-вопроса: {final_score}/100",
                    y
                )

            comment = analysis.get("comment")
            if comment:
                y = draw_paragraph(
                    c,
                    f"Комментарий эксперта: {comment}",
                    y
                )

            y -= 8
            if y < 80:
                c.showPage()
                y = 760


    # ------------------------------------------------
    # FOOTER
    # ------------------------------------------------
    c.setFont("Roboto", 9)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(
        40, 30,
        "Отчёт сгенерирован AI HR Interview System • Powered by FOTUR"
    )

    c.save()
    return filename
