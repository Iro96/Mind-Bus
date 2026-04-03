from typing import Dict, Any


def calculator_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    expression = args.get("expression")
    if not expression:
        return {"error": "No expression provided"}

    try:
        # Safe evaluator (numeric expressions only)
        allowed = {"__builtins__": None}
        result = eval(expression, allowed, {})
        return {"tool": "calculator", "expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e), "tool": "calculator"}
