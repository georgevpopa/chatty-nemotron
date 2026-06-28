"""Permission system — 3-tier trust model.
Levels:
  y  = allow this one command
  ya = allow all commands for this task (session)
  yw = trust this workspace permanently
  n  = deny
"""
import json
from pathlib import Path
from rich.console import Console

console = Console()

# Session-level: trust all for current task
_session_trust_all = False

# Transient in-memory override for Web UI mode
_auto_approve_override = False


def set_auto_approve_override(val: bool):
    global _auto_approve_override
    _auto_approve_override = val


def get_auto_approve_override() -> bool:
    return _auto_approve_override


# Workspace trust file
TRUST_FILE = Path.home() / ".chatty-chronos" / "trusted_workspaces"


def _load_trusted_workspaces() -> set:
    if TRUST_FILE.exists():
        return set(TRUST_FILE.read_text().strip().splitlines())
    return set()


def _save_trusted_workspace(path: str):
    workspaces = _load_trusted_workspaces()
    workspaces.add(path)
    TRUST_FILE.parent.mkdir(exist_ok=True)
    TRUST_FILE.write_text("\n".join(sorted(workspaces)) + "\n")


def is_workspace_trusted(cwd: str = None) -> bool:
    """Check if current workspace is permanently trusted."""
    if cwd is None:
        cwd = str(Path.cwd())
    trusted = _load_trusted_workspaces()
    # Check if cwd or any parent is trusted
    p = Path(cwd).resolve()
    while p != p.parent:
        if str(p) in trusted:
            return True
        p = p.parent
    return str(p) in trusted


def request_permission(tool_name: str, description: str, cwd: str = None) -> bool:
    """Ask user for permission via an interactive select menu. Returns True if allowed.
    
    Respects session trust and workspace trust.
    """
    global _session_trust_all, _auto_approve_override

    # In-memory transient override (for Web UI)
    if _auto_approve_override:
        return True

    # Session-level trust (ya was given earlier)
    if _session_trust_all:
        return True

    # Workspace-level trust
    if is_workspace_trusted(cwd):
        return True

    # Auto-approve from config (useful for Web UI)
    try:
        from core.config import Config
        cfg = Config()
        if cfg.get("auto_approve_tools", False):
            return True
    except Exception:
        pass

    # Ask user
    console.print(f"\n  [yellow]⚠ Permission required:[/yellow] [bold]{tool_name}[/bold]")
    console.print(f"  [dim]{description}[/dim]")

    # Map display labels to internal action codes
    _PERMISSION_CHOICES = {
        "Yes, allow once":               "y",
        "Yes to all (for this session)":  "ya",
        "Trust this workspace permanently": "yw",
        "No, deny":                      "n",
    }
    _LABELS = list(_PERMISSION_CHOICES.keys())

    try:
        import questionary
        selected_label = questionary.select(
            "  Allow execution?",
            choices=_LABELS,
            default=_LABELS[0],
        ).ask()
        choice = _PERMISSION_CHOICES.get(selected_label, "n") if selected_label else "n"
    except (KeyboardInterrupt, EOFError, ImportError):
        # Fallback to standard input if questionary is not available
        try:
            console.print(f"  [dim][y]es / [n]o / [ya] yes-all (session) / [yw] trust workspace[/dim]")
            choice = input("  Allow? ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return False

    if choice == "y" or choice == "yes":
        return True
    elif choice == "ya":
        _session_trust_all = True
        console.print("  [green]Trusted for this session.[/green]")
        return True
    elif choice == "yw":
        workspace = cwd or str(Path.cwd())
        _save_trusted_workspace(workspace)
        console.print(f"  [green]Workspace trusted permanently: {workspace}[/green]")
        return True
    else:
        console.print("  [red]Denied.[/red]")
        return False


def reset_session_trust():
    """Reset session-level trust (call on /clear or new task)."""
    global _session_trust_all
    _session_trust_all = False
