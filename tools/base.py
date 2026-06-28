"""Base tool interface — all tools inherit from this."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict = field(default_factory=dict)
    requires_permission: bool = True

    def execute(self, **kwargs) -> str:
        raise NotImplementedError

    def to_ollama_schema(self) -> dict:
        """Convert to Ollama tool call format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": [k for k, v in self.parameters.items() if v.get("required", False)],
                },
            },
        }
