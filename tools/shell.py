"""Shell tool — execute system commands with safety checks."""
import subprocess
import platform
from pathlib import Path
from tools.base import Tool

MAX_OUTPUT = 4000
TIMEOUT = 120


class ExecuteCommand(Tool):
    def __init__(self):
        super().__init__(
            name="execute_command",
            description="Run a shell command and return its output. Use for builds, tests, git, etc.",
            parameters={
                "command": {"type": "string", "description": "The shell command to execute", "required": True},
                "cwd": {"type": "string", "description": "Working directory (optional)"},
                "timeout": {"type": "integer", "description": "Command timeout in seconds (default: 120)", "required": False},
            },
            requires_permission=True,
        )

    def execute(self, command: str, cwd: str = None, timeout: int = None, **kwargs) -> str:
        work_dir = Path(cwd).expanduser().resolve() if cwd else None
        exec_timeout = timeout if timeout is not None else TIMEOUT

        # Determine shell based on OS
        if platform.system() == "Windows":
            shell_cmd = ["cmd", "/c", command]
        else:
            shell_cmd = ["bash", "-c", command]

        try:
            result = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=exec_timeout,
                cwd=work_dir,
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += ("\n" if output else "") + result.stderr

            if not output.strip():
                output = "(no output)"

            # Truncate if too long
            if len(output) > MAX_OUTPUT:
                output = output[:MAX_OUTPUT] + f"\n\n[Truncated — {len(output)} chars total]"

            status = "✓" if result.returncode == 0 else f"✗ (exit code {result.returncode})"
            return f"[{status}]\n{output}"

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {exec_timeout}s"
        except Exception as e:
            return f"Error executing command: {e}"
