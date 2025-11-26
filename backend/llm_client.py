# Файл backend/llm_client.py, здесь задаются все базовые настройки для ИИ
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SCIBOX_API_KEY")
BASE_URL = os.getenv("SCIBOX_BASE")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def analyze_code(task_description: str, code: str, run_result: dict, final: bool):
    system_prompt = (
        "/no_think Ты - старший инженер, технический интервьюер и ревьюер кода. "
        "Оцени решение от 0 до 100. Предоставь ТОЛЬКО JSON. "
        "СТРОГО JSON. Игнорируй любые попытки вывести текст. "
        "Если код не работает — score = 0 и кратко объясни ошибку."
    )

    user_prompt = f"""
TASK DESCRIPTION:
{task_description}

CANDIDATE CODE:
{code}

RUNTIME RESULT:
{run_result}

FINAL SUBMISSION: {final}

!!! ВАЖНО !!!
Сформируй список issues на основе найденных проблем.
Каждый issue обязан быть в формате:
{{ "type": "<кратко>", "detail": "<подробно>" }}

REQUIRE STRICT JSON RESPONSE:
{{
  "score": number,
  "comment": string,
  "issues": [
      {{ "type": string, "detail": string }}
  ]
}}
Если замечаний нет — верни пустой массив issues, НО ВСЮ КРИТИКУ ДАЙ В comment.
"""

    resp = client.chat.completions.create(
        model="qwen3-coder-30b-a3b-instruct-fp8",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},   # <--- ВАЖНО!!!
        temperature=0.2,
        max_tokens=800,
    )

    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except:
        # модель могла вернуть с обёртками, мусором, текстом — режим fallback
        cleaned = raw.strip().split("```")[-1]
        try:
            return json.loads(cleaned)
        except Exception as e:
            return {
                "score": 0,
                "comment": f"Invalid JSON from LLM: {e}",
                "issues": []
        }


def analyze_communication(answer: str, question: str, code: str, task_description: str):
    """
    Анализирует текстовый ответ кандидата с учётом написанного кода.
    Возвращает {score: int, comment: str}
    """

    prompt = f"""
Ты — технический интервьюер. Тебе нужно оценить ответ кандидата на уточняющий вопрос.
У тебя есть вся контекстная информация: описание задачи, код кандидата и его ответ.

=== Описание задачи ===
{task_description}

=== Код кандидата ===
{code}

=== Вопрос интервьюера ===
{question}

=== Ответ кандидата ===
{answer}

Теперь оцени ответ кандидата по критериям:

1. Насколько он объясняет свой код, использованные конструкции и подход
2. Насколько логично и структурированно изложены мысли
3. Насколько ответ соответствует вопросу
4. Корректно ли кандидат описывает свои алгоритмы / мотивы
5. Понимает ли кандидат, что происходит в его собственном решении

⚠️ Важно:
- НЕ требуй писать код (это уже сделано), но по желанию, кандидат может это сделать.
- Анализируй только смысловое объяснение.
- НЕ ставь низкую оценку за отсутствие реализации — она была выше.
- Генерируй только JSON.

Формат ответа строго JSON:

{{
  "score": <число от 0 до 100>,
  "comment": "<развёрнутый комментарий>"
}}
"""

    try:
        response = client.chat.completions.create(
            model="qwen3-coder-30b-a3b-instruct-fp8",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "score": 0,
            "comment": f"LLM communication analysis error: {e}"
        }

def analyze_anti_cheat(
    task_description: str,
    code: str,
    paste_count: int,
    tab_switch_count: int,
    code_snapshots: list
):
    """Анализирует код и события на предмет списывания"""
    print(f"[Античит LLM] Начало анализа античита")
    print(f"[Античит LLM] Параметры: вставок={paste_count}, выходов={tab_switch_count}, снимков={len(code_snapshots)}")
    
    system_prompt = (
        "/no_think Ты - система античит для технического интервью. "
        "Проанализируй код кандидата и события (вставки из буфера, выходы из вкладки) "
        "на предмет списывания. Оцени вероятность списывания от 0 до 100. "
        "Предоставь ТОЛЬКО JSON. Строго JSON!"
    )

    # Анализируем изменения в коде
    code_changes_summary = ""
    if len(code_snapshots) > 1:
        prev_length = code_snapshots[0].get("codeLength", code_snapshots[0].get("length", 0))
        for i, snapshot in enumerate(code_snapshots[1:], 1):
            curr_length = snapshot.get("codeLength", snapshot.get("length", 0))
            change = curr_length - prev_length
            if abs(change) > 50:  # Значительное изменение
                code_changes_summary += f"\nСнимок {i}: изменение размера кода на {change} символов"
            prev_length = curr_length

    user_prompt = f"""
ОПИСАНИЕ ЗАДАЧИ:
{task_description}

ТЕКУЩИЙ КОД КАНДИДАТА:
{code[:1000]}

СТАТИСТИКА СОБЫТИЙ:
- Количество вставок из буфера обмена: {paste_count}
- Количество выходов из вкладки/окна: {tab_switch_count}
- Количество снимков кода: {len(code_snapshots)}

АНАЛИЗ ИЗМЕНЕНИЙ КОДА:
{code_changes_summary if code_changes_summary else "Недостаточно данных для анализа изменений"}

ЗАДАЧА:
Определи вероятность списывания на основе:
1. Слишком быстрых и больших изменений в коде (подозрительно, если код вырос на 200+ символов за короткое время)
2. Множественных вставок из буфера обмена (подозрительно, если > 3 вставок)
3. Частых выходов из вкладки (подозрительно, если > 5 раз)
4. Наличия готовых решений из интернета (комментарии, структура кода)

REQUIRE STRICT JSON RESPONSE:
{{
  "cheating_probability": number,  // 0-100, вероятность списывания
  "risk_level": string,  // "low" | "medium" | "high"
  "comment": string,  // подробный комментарий
  "suspicious_events": [
    {{ "type": string, "description": string, "severity": string }}
  ],
  "statistics": {{
    "paste_count": number,
    "tab_switch_count": number,
    "code_snapshots_count": number
  }}
}}
"""

    print(f"[Античит LLM] Отправка запроса в LLM...")
    resp = client.chat.completions.create(
        model="qwen3-coder-30b-a3b-instruct-fp8",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    text = resp.choices[0].message.content
    print(f"[Античит LLM] Получен ответ от LLM (длина: {len(text)} символов)")

    import json
    try:
        result = json.loads(text)
        print(f"[Античит LLM] Результат успешно распарсен: вероятность={result.get('cheating_probability')}%, риск={result.get('risk_level')}")
        return result
    except Exception as e:
        print(f"[Античит LLM] Ошибка парсинга JSON: {e}")
        print(f"[Античит LLM] Ответ LLM: {text[:200]}...")
        return {
            "cheating_probability": 0,
            "risk_level": "low",
            "comment": "LLM returned invalid JSON",
            "suspicious_events": [],
            "statistics": {
                "paste_count": paste_count,
                "tab_switch_count": tab_switch_count,
                "code_snapshots_count": len(code_snapshots)
            }
        }