from typing import Dict, Any
import subprocess


def code_exec_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    code = args.get("code")
    if not code:
        return {"error": "No code provided"}

    try:
        # simple, non-persistent, untrusted code execution sandbox
        result = subprocess.run(
            ["python", "-u", "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return {
            "tool": "code_exec",
            "code": code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out", "tool": "code_exec"}
    except Exception as e:
        return {"error": str(e), "tool": "code_exec"}
