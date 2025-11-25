# Файл backend/llm_client.py, здесь задаются все базовые настройки для ИИ
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SCIBOX_API_KEY")
BASE_URL = os.getenv("SCIBOX_BASE")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def analyze_code(task_description: str, code: str, run_result: dict, final: bool):
    system_prompt = (
        "/no_think Ты - старший инженер, технический интервьюер и ревьюер кода."
        "Оцени решение от 0 до 100. Предоставь ТОЛЬКО JSON."
    )

    user_prompt = f"""
TASK DESCRIPTION:
{task_description}

CANDIDATE CODE:
{code}

RUNTIME RESULT:
{run_result}

FINAL SUBMISSION: {final}

REQUIRE STRICT JSON RESPONSE:
{{
  "score": number,
  "comment": string,
  "issues": [ {{ "type": string, "detail": string }} ]
}}
"""

    resp = client.chat.completions.create(
        model="qwen3-coder-30b-a3b-instruct-fp8",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=800,
    )

    text = resp.choices[0].message.content

    # Попытка распарсить JSON
    import json
    try:
        return json.loads(text)
    except:
        return {
            "score": 0,
            "comment": "LLM returned invalid JSON",
            "issues": [{"type": "llm", "detail": text}]
        }
