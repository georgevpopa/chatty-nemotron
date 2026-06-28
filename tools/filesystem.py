"""Filesystem tools — read, write, search_replace, list_directory, glob, move_file."""
import os
import shutil
import glob as glob_module
from pathlib import Path
from tools.base import Tool


class ReadFile(Tool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. Returns the full text content.",
            parameters={
                "path": {"type": "string", "description": "Path to the file to read", "required": True},
            },
            requires_permission=False,
        )

    def execute(self, path: str, **kwargs) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {p}"
        if not p.is_file():
            return f"Error: Not a file: {p}"
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            if len(content) > 50000:
                return content[:50000] + f"\n\n[Truncated — file is {len(content)} chars]"
            return content
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFile(Tool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Create, overwrite, or append content to a file.",
            parameters={
                "path": {"type": "string", "description": "Path to the file to write", "required": True},
                "content": {"type": "string", "description": "Content to write", "required": True},
                "mode": {"type": "string", "description": "Mode: 'w' for overwrite (default), 'a' for append", "required": False},
            },
            requires_permission=True,
        )

    def execute(self, path: str, content: str, mode: str = "w", **kwargs) -> str:
        p = Path(path).expanduser().resolve()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # Daca modul este 'a', adaugam la finalul fisierului
            write_mode = "a" if mode == "a" else "w"
            with open(p, write_mode, encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} chars to {p} (mode: {write_mode})"
        except Exception as e:
            return f"Error writing file: {e}"


class SearchReplace(Tool):
    def __init__(self):
        super().__init__(
            name="search_replace",
            description="Replace an exact string in a file. Safer than full rewrite.",
            parameters={
                "path": {"type": "string", "description": "Path to the file", "required": True},
                "old_text": {"type": "string", "description": "Exact text to find", "required": True},
                "new_text": {"type": "string", "description": "Replacement text", "required": True},
            },
            requires_permission=True,
        )

    def execute(self, path: str, old_text: str, new_text: str, **kwargs) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {p}"
        content = p.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {p.name}"
        count = content.count(old_text)
        new_content = content.replace(old_text, new_text)
        p.write_text(new_content, encoding="utf-8")
        return f"Replaced {count} occurrence(s) in {p.name}"


class ListDirectory(Tool):
    def __init__(self):
        super().__init__(
            name="list_directory",
            description="List files and directories at the given path.",
            parameters={
                "path": {"type": "string", "description": "Directory path to list", "required": True},
            },
            requires_permission=False,
        )

    def execute(self, path: str, **kwargs) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: Path not found: {p}"
        if not p.is_dir():
            return f"Error: Not a directory: {p}"
        entries = []
        try:
            for item in sorted(p.iterdir()):
                prefix = "[DIR] " if item.is_dir() else "      "
                entries.append(f"{prefix}{item.name}")
            if not entries:
                return f"{p}: (empty directory)"
            return f"{p}:\n" + "\n".join(entries[:100])
        except Exception as e:
            return f"Error listing directory: {e}"


class GlobSearch(Tool):
    def __init__(self):
        super().__init__(
            name="glob_search",
            description="Find files matching a glob pattern (e.g. '**/*.py').",
            parameters={
                "pattern": {"type": "string", "description": "Glob pattern", "required": True},
                "path": {"type": "string", "description": "Base directory (default: current dir)"},
            },
            requires_permission=False,
        )

    def execute(self, pattern: str, path: str = ".", **kwargs) -> str:
        base = Path(path).expanduser().resolve()
        matches = list(base.glob(pattern))[:50]
        if not matches:
            return f"No files matching '{pattern}' in {base}"
        result = f"Found {len(matches)} file(s):\n"
        result += "\n".join(f"  {m.relative_to(base)}" for m in matches)
        return result


class Grep(Tool):
    def __init__(self):
        super().__init__(
            name="grep",
            description="Search for a text pattern in files. Returns matching lines with file:line format.",
            parameters={
                "pattern": {"type": "string", "description": "Text pattern to search for", "required": True},
                "path": {"type": "string", "description": "Directory or file to search in", "required": True},
                "include": {"type": "string", "description": "File glob filter (e.g. '*.py')"},
            },
            requires_permission=False,
        )

    def execute(self, pattern: str, path: str = ".", include: str = None, **kwargs) -> str:
        base = Path(path).expanduser().resolve()
        if base.is_file():
            files = [base]
        elif base.is_dir():
            glob_pat = include or "*"
            files = list(base.rglob(glob_pat))[:200]
        else:
            return f"Error: Path not found: {base}"

        results = []
        for f in files:
            if not f.is_file():
                continue
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
                for i, line in enumerate(lines, 1):
                    if pattern.lower() in line.lower():
                        rel = f.relative_to(base) if base.is_dir() else f.name
                        results.append(f"{rel}:{i}: {line.strip()}")
                        if len(results) >= 50:
                            break
            except Exception:
                continue
            if len(results) >= 50:
                break

        if not results:
            return f"No matches for '{pattern}' in {base}"
        return f"Found {len(results)} match(es):\n" + "\n".join(results)


class MoveFile(Tool):
    def __init__(self):
        super().__init__(
            name="move_file",
            description="Move or rename a file or directory on Windows. Automatically creates missing target folders.",
            parameters={
                "src_path": {"type": "string", "description": "Absolute or relative path to the source file", "required": True},
                "dst_folder": {"type": "string", "description": "The destination directory where the file should be moved", "required": True},
            },
            requires_permission=True,
        )

    def execute(self, src_path: str, dst_folder: str, **kwargs) -> str:
        src = Path(src_path).expanduser().resolve()
        dst_dir = Path(dst_folder).expanduser().resolve()

        if not src.exists():
            return f"Error: Source path does not exist: {src}"

        try:
            # Creare structură foldere destinație (echivalent mkdir -p)
            if not dst_dir.exists():
                dst_dir.mkdir(parents=True, exist_ok=True)
            
            final_dst = dst_dir / src.name
            
            # Execuție nativă cross-partition sigură pentru Windows 11
            shutil.move(str(src), str(final_dst))
            return f"Success: Moved '{src.name}' into '{dst_dir}'"
        except Exception as e:
            return f"Error executing move_file: {str(e)}"