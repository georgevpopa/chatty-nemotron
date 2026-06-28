"""Sub-agent delegator — spawns child agents for parallel subtasks."""
from rich.console import Console
from core.config import Config

console = Console()

MAX_DEPTH = 2


def delegate_task(task: str, config: Config, depth: int = 0, max_iterations: int = 10) -> str:
    """Spawn a child agent to handle a subtask.

    Args:
        task: The subtask description
        config: Config instance
        depth: Current delegation depth (prevents infinite recursion)
        max_iterations: Max steps for child agent

    Returns:
        Result text from the child agent
    """
    if depth >= MAX_DEPTH:
        return "Error: Maximum delegation depth reached. Cannot delegate further."

    console.print(f"  [cyan]Delegating subtask (depth {depth + 1})...[/cyan]")
    console.print(f"  [dim]{task[:80]}{'...' if len(task) > 80 else ''}[/dim]")

    from core.agent import ReActAgent
    agent = ReActAgent(config, max_iterations=max_iterations, depth=depth + 1)
    result = agent.run(task)
    return result
