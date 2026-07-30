import subprocess
import tempfile
from pathlib import Path
from dataset import download, load

app_dir = Path(__file__).parent.resolve()


def run_python(code: str):
    workdir = Path(tempfile.mkdtemp())
    script = workdir / "script.py"

    script.write_text(
        f"import sys\nsys.path.insert(0, {repr(str(app_dir))})\n"
        "from dataset import download, load\n\n"
        + code
        + "\n\ntry:\n    print(result)\nexcept NameError:\n    pass\n"
    )

    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=workdir,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "workdir": str(workdir),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out",
            "returncode": -1,
            "workdir": str(workdir),
        }



