import json
import subprocess
import tempfile
import textwrap
from typing import Any, Dict, List


# ==============================================================
#  JS SANDBOX
# ==============================================================

def run_js_in_sandbox(code: str) -> Any:
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as f:
        f.write(code)
        filename = f.name

    try:
        proc = subprocess.run(
            ["node", filename],
            capture_output=True,
            text=True,
            timeout=2
        )
        if proc.returncode != 0:
            return {"error": proc.stderr.strip()}
        return {"stdout": proc.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


def generate_js_test_wrapper(code: str, func_name: str, args: list):
    js_args = []
    for a in args:
        if a == "NaN":
            js_args.append("NaN")
        else:
            js_args.append(json.dumps(a))
    
    arg_literal = ",".join(js_args)

    return f"""
{code}

try {{
  const result = {func_name}({arg_literal});
  console.log(JSON.stringify({{"result": result}}));
}} catch (e) {{
  console.error("ERROR:" + e.toString());
}}
"""


def run_tests_js(task_id: str, code: str, test_bank: Dict[str, Any]):
    tests = test_bank.get(task_id)
    if not tests:
        return []

    all_results = []

    # имя функции из первой строки
    first_line = code.split("\n")[0]
    func_name = first_line.replace("function", "").split("(")[0].strip()

    # visible
    for idx, test in enumerate(tests["visible"], start=1):
        wrapped_js = generate_js_test_wrapper(code, func_name, test["input"])
        result = run_js_in_sandbox(wrapped_js)

        passed = False
        if "stdout" in result:
            try:
                parsed = json.loads(result["stdout"])
                passed = parsed["result"] == test["expected"]
            except:
                passed = False

        all_results.append({
            "name": f"Test #{idx}",
            "passed": passed,
            "visible": True
        })

    # hidden
    for idx, test in enumerate(tests["hidden"], start=1):
        wrapped_js = generate_js_test_wrapper(code, func_name, test["input"])
        result = run_js_in_sandbox(wrapped_js)

        passed = False
        if "stdout" in result:
            try:
                parsed = json.loads(result["stdout"])
                passed = parsed["result"] == test["expected"]
            except:
                passed = False

        all_results.append({
            "name": f"Hidden #{idx}",
            "passed": passed,
            "visible": False
        })

    return all_results



# ==============================================================
#  PYTHON SANDBOX
# ==============================================================

def run_py_in_sandbox(code: str) -> Any:
    """
    Выполняет Python-код в отдельном процессе и возвращает stdout или ошибку.
    """
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write(code)
        filename = f.name

    try:
        proc = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True,
            timeout=2
        )
        if proc.returncode != 0:
            return {"error": proc.stderr.strip()}
        return {"stdout": proc.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}



def generate_py_test_wrapper(code: str, func_name: str, args: list):
    """
    Генерирует Python-код: функция кандидата + тест + вывод JSON.
    """
    # args → передаём literal: [1,2] → 1,2
    arg_literal = json.dumps(args)[1:-1]

    wrapped = f"""
{code}

import json

try:
    result = {func_name}({arg_literal})
    print(json.dumps({{"result": result}}))
except Exception as e:
    print("ERROR:" + str(e))
"""

    return textwrap.dedent(wrapped)



def detect_python_function_name(code: str) -> str:
    """
    Из первой строки вида:
        def add(a,b):
    → извлекает имя функции: "add"
    """
    for line in code.split("\n"):
        line = line.strip()
        if line.startswith("def "):
            return line.replace("def", "").split("(")[0].strip()
    return "func"


def run_tests_py(task_id: str, code: str, test_bank: Dict[str, Any]):
    tests = test_bank.get(task_id)
    if not tests:
        return []

    all_results: List[Dict[str, Any]] = []

    func_name = detect_python_function_name(code)

    # visible tests
    for idx, test in enumerate(tests["visible"], start=1):
        wrapped_py = generate_py_test_wrapper(code, func_name, test["input"])
        result = run_py_in_sandbox(wrapped_py)

        passed = False
        if "stdout" in result:
            try:
                parsed = json.loads(result["stdout"])
                passed = parsed["result"] == test["expected"]
            except Exception:
                passed = False

        all_results.append({
            "name": f"Test #{idx}",
            "passed": passed,
            "visible": True
        })

    # hidden tests
    for idx, test in enumerate(tests["hidden"], start=1):
        wrapped_py = generate_py_test_wrapper(code, func_name, test["input"])
        result = run_py_in_sandbox(wrapped_py)

        passed = False
        if "stdout" in result:
            try:
                parsed = json.loads(result["stdout"])
                passed = parsed["result"] == test["expected"]
            except Exception:
                passed = False

        all_results.append({
            "name": f"Hidden #{idx}",
            "passed": passed,
            "visible": False
        })

    return all_results
