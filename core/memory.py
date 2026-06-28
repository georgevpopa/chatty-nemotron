"""Persistent memory — facts that survive across sessions."""
import json
from pathlib import Path


class Memory:
    def __init__(self):
        self.path = Path.home() / ".chatty-chronos" / "memory.json"
        self.facts = self._load()

    def _load(self) -> list[str]:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save(self):
        self.path.parent.mkdir(exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.facts, f, indent=2, ensure_ascii=False)

    def add(self, fact: str):
        if fact not in self.facts:
            self.facts.append(fact)
            self.save()

    def remove(self, index: int) -> bool:
        if 0 <= index < len(self.facts):
            self.facts.pop(index)
            self.save()
            return True
        return False

    def clear(self):
        self.facts = []
        self.save()

    def get_context(self) -> str:
        """Format memory for injection into system prompt."""
        if not self.facts:
            return ""
        lines = "\n".join(f"- {f}" for f in self.facts)
        return f"\n## Things you should remember:\n{lines}\n"
