"""Agent delegation tool — exposes sub-agent spawning to the LLM."""
from tools.base import Tool
from core.config import Config
from core.delegator import delegate_task


class DelegateSubtask(Tool):
    def __init__(self):
        super().__init__(
            name="delegate_subtask",
            description=(
                "Delegate a specific technical subtask to a new autonomous child agent. "
                "Returns the child agent's final response/summary. Useful for parallelizing "
                "or isolating complex subtasks (e.g. compiling, scanning directories, or "
                "writing test files in isolation)."
            ),
            parameters={
                "task": {
                    "type": "string",
                    "description": "Detailed prompt or task description for the sub-agent.",
                    "required": True,
                }
            },
            requires_permission=True,
        )

    def execute(self, task: str, config: Config = None, depth: int = 0, **kwargs) -> str:
        if not config:
            config = Config()
        return delegate_task(task, config, depth=depth)
