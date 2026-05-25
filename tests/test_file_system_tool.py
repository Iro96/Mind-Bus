import os
from pathlib import Path

import pytest

import tools.file_system as file_system


@pytest.fixture
def workspace_root(tmp_path, monkeypatch):
    monkeypatch.setattr(file_system, "WORKSPACE_ROOT", tmp_path)
    return tmp_path


def test_file_system_resolve_path_normalizes_and_rejects_escape(workspace_root):
    target = workspace_root / "docs" / "guide.txt"
    target.parent.mkdir(parents=True)
    target.write_text("hello", encoding="utf-8")

    result = file_system.file_system_tool({"action": "resolve_path", "path": "./docs/../docs/guide.txt"})

    assert result["success"] is True
    assert result["path"] == str(target)

    escaped = file_system.file_system_tool({"action": "resolve_path", "path": "../outside.txt"})

    assert escaped["success"] is False
    assert "outside workspace" in escaped["error"].lower()


def test_file_system_read_list_and_tree_success(workspace_root):
    nested = workspace_root / "alpha" / "beta"
    nested.mkdir(parents=True)
    (workspace_root / "alpha" / "root.txt").write_text("root", encoding="utf-8")
    (nested / "child.txt").write_text("child", encoding="utf-8")

    read_result = file_system.file_system_tool({"action": "read_text", "path": "alpha/root.txt"})
    list_result = file_system.file_system_tool({"action": "list_dir", "path": "alpha"})
    tree_result = file_system.file_system_tool({"action": "tree", "path": "alpha", "max_depth": 2})

    assert read_result["success"] is True
    assert read_result["content"] == "root"
    assert list_result["success"] is True
    assert "root.txt" in list_result["entries"]
    assert "beta" in list_result["entries"]
    assert tree_result["success"] is True
    assert tree_result["entries"]


def test_file_system_write_gating_disabled_by_default(workspace_root, monkeypatch):
    monkeypatch.delenv("ENABLE_FILE_SYSTEM_WRITE", raising=False)

    result = file_system.file_system_tool({"action": "write_text", "path": "scratch.txt", "content": "hello"})

    assert result["success"] is False
    assert result["available"] is True
    assert "disabled" in result["error"].lower()
    assert not (workspace_root / "scratch.txt").exists()


def test_file_system_write_enabled_allows_create_and_edit(workspace_root, monkeypatch):
    monkeypatch.setenv("ENABLE_FILE_SYSTEM_WRITE", "1")

    created = file_system.file_system_tool({"action": "write_text", "path": "notes.txt", "content": "hello"})
    appended = file_system.file_system_tool({"action": "append_text", "path": "notes.txt", "content": " world"})
    updated = file_system.file_system_tool({"action": "replace_text", "path": "notes.txt", "old_text": "hello", "new_text": "hi"})

    assert created["success"] is True
    assert appended["success"] is True
    assert updated["success"] is True
    assert updated["replacements"] == 1
    assert (workspace_root / "notes.txt").read_text(encoding="utf-8") == "hi world"


def test_file_system_move_and_delete_behavior(workspace_root, monkeypatch):
    monkeypatch.setenv("ENABLE_FILE_SYSTEM_WRITE", "1")

    source = workspace_root / "source.txt"
    source.write_text("move me", encoding="utf-8")
    moved = file_system.file_system_tool({"action": "move_path", "path": "source.txt", "destination": "dest.txt"})
    deleted = file_system.file_system_tool({"action": "delete_path", "path": "dest.txt"})

    assert moved["success"] is True
    assert deleted["success"] is True
    assert not source.exists()
    assert not (workspace_root / "dest.txt").exists()


def test_file_system_replace_text_requires_old_text(workspace_root, monkeypatch):
    monkeypatch.setenv("ENABLE_FILE_SYSTEM_WRITE", "1")
    (workspace_root / "replace-me.txt").write_text("hello", encoding="utf-8")

    result = file_system.file_system_tool({"action": "replace_text", "path": "replace-me.txt", "new_text": "bye"})

    assert result["success"] is False
    assert "old_text" in result["error"].lower()


def test_file_system_power_shell_unavailable_falls_back(monkeypatch, workspace_root):
    monkeypatch.setattr(file_system, "_detect_powershell", lambda: None)

    result = file_system.file_system_tool({"action": "read_text", "path": "README.md"})

    assert result["available"] is False
    assert result["tool"] == "file_system"


@pytest.mark.skipif(file_system._detect_powershell() is None, reason="PowerShell is not available")
def test_file_system_integration_uses_discovered_powershell():
    root = Path(__file__).resolve().parents[1]
    result = file_system.file_system_tool({"action": "read_text", "path": str(root / "README.md")})

    assert result["success"] is True
    assert result["content"]
