"""Safety policy shared by the analysis scripts and the executor.

Guard idea derived from CharlesLadera/disk-cleanup tests/test_safety.py
(MIT, Copyright (c) 2026 Charles Ladera). See NOTICE.

Banned words are assembled from fragments so that this file itself does not
trip the source guard it defines.
"""
import re

_J = "".join

# Python-level primitives that delete, move or rename files.
_SOURCE_PATTERNS = [
    re.escape(_J(["shutil.", "rmtree"])),
    re.escape(_J(["shutil.", "move"])),
    re.escape(_J(["os.", "remove"])) + r"\b",
    re.escape(_J(["os.", "unlink"])),
    re.escape(_J(["os.", "rm", "dir"])),
    re.escape(_J(["os.", "removedirs"])),
    re.escape(_J(["os.", "rename"])),
    re.escape(_J(["os.", "replace"])),
    r"\." + _J(["un", "link"]) + r"\(",
    r"\." + _J(["rm", "dir"]) + r"\(",
    r"\." + _J(["re", "name"]) + r"\(",
    _J(["send2", "trash"]),
    _J(["SHFile", "Operation"]),
    _J(["Delete", "File"]),
    _J(["Remove", "-Item"]),
    _J(["Clear", "-RecycleBin"]),
    _J(["Move", "-Item"]),
    r"""['"\s/]""" + _J(["d", "el"]) + r"""['"\s]""",
    r"""['"\s/]""" + _J(["r", "d"]) + r"""['"\s]""",
    r"""['"\s/]""" + _J(["rm", "dir"]) + r"""['"\s]""",
    _J(["task", "kill"]),
]
_SOURCE_RE = [re.compile(p, re.IGNORECASE) for p in _SOURCE_PATTERNS]


def source_violations(text):
    """Return the deletion/move primitives found in Python source text."""
    return [p.pattern for p in _SOURCE_RE if p.search(text)]


# Each command the skill may run is matched as a whole against an exact template:
# no extra options, no extra arguments, no shell metacharacters.
_COMMAND_TEMPLATES = [
    re.compile(r"^npm cache verify$"),
    re.compile(r"^npm cache clean --force$"),
    re.compile(r"^pnpm store prune$"),
    re.compile(r"^uv cache prune$"),
    re.compile(r"^dotnet nuget locals http-cache --clear$"),
    re.compile(r"^nvm uninstall( \d+\.\d+\.\d+)?$"),
    re.compile(r"^docker builder prune -f$"),
    re.compile(r"^docker image prune -f$"),
]


def command_violations(command):
    """Problems with a command the skill may run directly (empty = allowed)."""
    if any(t.fullmatch(command) for t in _COMMAND_TEMPLATES):
        return []
    return ["command does not exactly match a vetted template"]


_HANDOFF_SHAPES = [
    re.compile(r"^pnputil /delete-driver oem\d+\.inf$", re.IGNORECASE),
    re.compile(r"^Dism /Online /Cleanup-Image /StartComponentCleanup$", re.IGNORECASE),
    re.compile(r"^wsl --manage [A-Za-z0-9_.-]+ --set-sparse true$"),
]


def handoff_violations(command):
    """Problems with a command handed to the user to run as administrator."""
    if any(s.match(command) for s in _HANDOFF_SHAPES):
        return []
    return ["not one of the fixed administrator command shapes"]
