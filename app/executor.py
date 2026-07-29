import subprocess
import tempfile
from pathlib import Path
import io
import contextlib
import traceback

def run_python(code: str):
    code += "\n\ntry:\n    print(result)\nexcept NameError:\n    pass\n"

    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "script.py"
        script.write_text(code)

        try:
            result = subprocess.run(
                ["python3", str(script)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stderr": "Execution timed out",
            }
