import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
WRITE_ENV = "ENABLE_FILE_SYSTEM_WRITE"


def _detect_powershell() -> Optional[str]:
    for command in ("pwsh", "powershell"):
        if shutil.which(command):
            return command
    return None


def _is_write_enabled() -> bool:
    return os.getenv(WRITE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_path(raw_path: Any) -> Path:
    if raw_path is None:
        raise ValueError("path is required")

    candidate = str(raw_path).strip()
    if not candidate:
        raise ValueError("path is required")

    base = Path(candidate)
    if not base.is_absolute():
        base = WORKSPACE_ROOT / base

    resolved = base.resolve(strict=False)
    root = WORKSPACE_ROOT.resolve()

    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("path is outside workspace") from exc

    return resolved


def _build_error(message: str, *, available: bool = True) -> Dict[str, Any]:
    return {
        "tool": "file_system",
        "available": available,
        "success": False,
        "error": message,
    }


def _run_powershell(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    command = _detect_powershell()
    if command is None:
        return _build_error("PowerShell is unavailable", available=False)

    script = r'''
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8

$payload = [System.Console]::In.ReadToEnd()
$input = $payload | ConvertFrom-Json
$action = [string]$input.action
$path = [string]$input.path
$destination = if ($null -ne $input.destination) { [string]$input.destination } else { $null }
$content = if ($null -ne $input.content) { [string]$input.content } else { $null }
$oldText = if ($null -ne $input.old_text) { [string]$input.old_text } else { $null }
$newText = if ($null -ne $input.new_text) { [string]$input.new_text } else { $null }
$recursive = [bool]$input.recursive
$maxDepth = if ($null -ne $input.max_depth) { [int]$input.max_depth } else { 4 }
$maxItems = if ($null -ne $input.max_items) { [int]$input.max_items } else { 200 }
$maxChars = if ($null -ne $input.max_chars) { [int]$input.max_chars } else { 20000 }

function Write-Result($result) {
    $json = $result | ConvertTo-Json -Depth 20
    [Console]::Write($json)
}

switch ($action) {
    "read_text" {
        $text = Get-Content -LiteralPath $path -Raw -Encoding utf8
        $truncated = $text.Length -gt $maxChars
        if ($truncated) {
            $text = $text.Substring(0, $maxChars)
        }
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            content = $text
            truncated = $truncated
            chars = $text.Length
        })
    }
    "list_dir" {
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            throw "path is not a directory"
        }
        $entries = Get-ChildItem -LiteralPath $path -Force | Select-Object -ExpandProperty Name
        $truncated = $entries.Count -gt $maxItems
        if ($truncated) {
            $entries = $entries[0..($maxItems - 1)]
        }
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            entries = $entries
            count = $entries.Count
            truncated = $truncated
        })
    }
    "tree" {
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            throw "path is not a directory"
        }
        $entries = Get-ChildItem -LiteralPath $path -Force -Recurse -Depth $maxDepth | Select-Object -ExpandProperty FullName
        $truncated = $entries.Count -gt $maxItems
        if ($truncated) {
            $entries = $entries[0..($maxItems - 1)]
        }
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            entries = $entries
            count = $entries.Count
            truncated = $truncated
        })
    }
    "write_text" {
        Set-Content -LiteralPath $path -Value $content -Encoding utf8
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            chars = $content.Length
        })
    }
    "append_text" {
        Add-Content -LiteralPath $path -Value $content -Encoding utf8
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            chars = $content.Length
        })
    }
    "replace_text" {
        if ([string]::IsNullOrWhiteSpace($oldText)) {
            throw "old_text is required"
        }
        $current = Get-Content -LiteralPath $path -Raw -Encoding utf8
        if ($current -notlike "*$oldText*") {
            throw "old_text not found"
        }
        $updated = $current.Replace($oldText, $newText)
        $replacements = ([regex]::Matches($current, [regex]::Escape($oldText))).Count
        Set-Content -LiteralPath $path -Value $updated -Encoding utf8
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            replacements = $replacements
        })
    }
    "make_dir" {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Result(@{
            success = $true
            action = $action
            path = $path
        })
    }
    "move_path" {
        Move-Item -LiteralPath $path -Destination $destination
        Write-Result(@{
            success = $true
            action = $action
            path = $path
            destination = $destination
        })
    }
    "delete_path" {
        if (Test-Path -LiteralPath $path -PathType Container) {
            $children = Get-ChildItem -LiteralPath $path -Force
            if ($children.Count -gt 0 -and -not $recursive) {
                throw "recursive=true is required for non-empty directories"
            }
        }
        Remove-Item -LiteralPath $path -Force -Recurse:$recursive
        Write-Result(@{
            success = $true
            action = $action
            path = $path
        })
    }
    default {
        throw "unsupported action"
    }
}
'''

    try:
        completed = subprocess.run(
            [command, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return _build_error(f"PowerShell execution failed: {exc}")

    stdout = completed.stdout.decode("utf-8", errors="replace")
    stderr = completed.stderr.decode("utf-8", errors="replace")

    if completed.returncode != 0:
        message = stderr.strip() or stdout.strip() or f"PowerShell exited with code {completed.returncode}"
        return _build_error(message)

    if not stdout.strip():
        return _build_error("PowerShell returned no output")

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return _build_error(f"PowerShell output parse failed: {exc}")

    if not isinstance(parsed, dict):
        return _build_error("PowerShell returned invalid JSON")

    return parsed


def file_system_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(args or {})
    action = str(payload.get("action", "")).strip()

    if not action:
        return _build_error("action is required")

    if action == "resolve_path":
        try:
            path = _normalize_path(payload.get("path"))
            return {
                "tool": "file_system",
                "available": True,
                "success": True,
                "action": action,
                "path": str(path),
            }
        except ValueError as exc:
            return _build_error(str(exc))

    if action in {"write_text", "append_text", "replace_text", "make_dir", "move_path", "delete_path"} and not _is_write_enabled():
        return _build_error("file system write is disabled")

    try:
        path = _normalize_path(payload.get("path"))
    except ValueError as exc:
        return _build_error(str(exc))

    if action == "delete_path":
        recursive = bool(payload.get("recursive", False))
        if path.exists() and path.is_dir() and any(path.iterdir()) and not recursive:
            return _build_error("recursive=true is required for non-empty directories")

    script_payload = {
        "action": action,
        "path": str(path),
        "destination": str(_normalize_path(payload.get("destination"))) if payload.get("destination") else None,
        "content": payload.get("content"),
        "old_text": payload.get("old_text"),
        "new_text": payload.get("new_text"),
        "recursive": bool(payload.get("recursive", False)),
        "max_depth": payload.get("max_depth", 4),
        "max_items": payload.get("max_items", 200),
        "max_chars": payload.get("max_chars", 20000),
    }

    result = _run_powershell(action, script_payload)

    if result.get("available") is False:
        return result

    if result.get("success") is False:
        return result

    if action == "read_text":
        content = result.get("content") or ""
        max_chars = int(script_payload["max_chars"])
        truncated = bool(result.get("truncated", False)) or len(content) > max_chars
        if len(content) > max_chars:
            content = content[:max_chars]
        return {
            "tool": "file_system",
            "available": True,
            "success": True,
            "action": action,
            "path": str(path),
            "content": content,
            "truncated": truncated,
            "chars": len(content),
        }

    if action in {"list_dir", "tree"}:
        entries = result.get("entries") or []
        max_items = int(script_payload["max_items"])
        truncated = bool(result.get("truncated", False)) or len(entries) > max_items
        if len(entries) > max_items:
            entries = entries[:max_items]
        return {
            "tool": "file_system",
            "available": True,
            "success": True,
            "action": action,
            "path": str(path),
            "entries": entries,
            "count": len(entries),
            "truncated": truncated,
        }

    if action == "replace_text":
        return {
            "tool": "file_system",
            "available": True,
            "success": True,
            "action": action,
            "path": str(path),
            "replacements": int(result.get("replacements", 0)),
        }

    if action in {"write_text", "append_text"}:
        return {
            "tool": "file_system",
            "available": True,
            "success": True,
            "action": action,
            "path": str(path),
            "chars": int(result.get("chars", 0)),
        }

    if action == "move_path":
        return {
            "tool": "file_system",
            "available": True,
            "success": True,
            "action": action,
            "path": str(path),
            "destination": str(_normalize_path(payload.get("destination"))),
        }

    return {
        "tool": "file_system",
        "available": True,
        "success": True,
        "action": action,
        "path": str(path),
    }
