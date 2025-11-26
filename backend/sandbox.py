# backend/sandbox.py файл для запуска кода кандидата в песочнице
import subprocess
import tempfile
import time
import os
import sys

def run_js(code: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as f:
        f.write(code.encode("utf-8"))
        f.flush()
        path = f.name

    start = time.time()
    try:
        proc = subprocess.Popen(
            ["node", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False   # читаем байты, не строки
        )

        stdout_bytes, stderr_bytes = proc.communicate(timeout=3)

        # Декодируем ВСЕГДА как UTF-8
        stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

        return {
            "stdout": stdout,
            "stderr": stderr,
            "metrics": {"exec_time_ms": int((time.time() - start)*1000)}
        }

    except subprocess.TimeoutExpired:
        proc.kill()
        return {"error": "Timeout"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        os.remove(path)

# ---------------------------------------------------
#  PY SANDBOX
# ---------------------------------------------------
def run_py(code: str):
    """
    Песочница для Python.
    Запускает код через системный Python.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode("utf-8"))
        path = f.name

    start = time.time()

    try:
        proc = subprocess.Popen(
            [sys.executable, path],       # запускаем текущий Python
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = proc.communicate(timeout=3)

        return {
            "stdout": stdout,
            "stderr": stderr,
            "metrics": {
                "exec_time_ms": int((time.time() - start) * 1000)
            }
        }

    except subprocess.TimeoutExpired:
        proc.kill()
        return {"error": "Timeout"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        try:
            os.remove(path)
        except:
            pass