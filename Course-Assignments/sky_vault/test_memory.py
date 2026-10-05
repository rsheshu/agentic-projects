import json

import memory


def test_memory_persists_and_overwrites(tmp_path, monkeypatch):
    memory_path = tmp_path / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_PATH", memory_path)
    memory.clear_memory()

    memory.remember("prefers_terminal", "Terminal 2", "user")
    assert memory.recall("Terminal 2")["key"] == "prefers_terminal"

    memory.remember("prefers_terminal", "Terminal 3", "user")
    data = json.loads(memory_path.read_text(encoding="utf-8"))
    assert data["prefers_terminal"]["value"] == "Terminal 3"
    assert memory.recall("Terminal 2") == {}


def test_memory_summary_includes_loaded_facts(tmp_path, monkeypatch):
    memory_path = tmp_path / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_PATH", memory_path)
    memory.clear_memory()

    memory.remember("preferred_gate_terminal", "Terminal 2", "user")
    summary = memory.load_memory_summary()

    assert "preferred_gate_terminal" in summary
    assert "Terminal 2" in summary
