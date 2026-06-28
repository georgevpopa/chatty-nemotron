"""Tool registry — discovers and provides all available tools."""
from tools.filesystem import ReadFile, WriteFile, SearchReplace, ListDirectory, GlobSearch, Grep, MoveFile
from tools.shell import ExecuteCommand
from tools.agent_delegator import DelegateSubtask


def get_all_tools():
    """Return all available tool instances."""
    return [
        ReadFile(),
        WriteFile(),
        SearchReplace(),
        ListDirectory(),
        GlobSearch(),
        Grep(),
        MoveFile(),
        ExecuteCommand(),
        DelegateSubtask(),
    ]


def get_tool_by_name(name: str):
    """Find a tool by its name."""
    for tool in get_all_tools():
        if tool.name == name:
            return tool
    return None


def get_ollama_tools_schema():
    """Get all tools in Ollama-compatible format."""
    return [t.to_ollama_schema() for t in get_all_tools()]