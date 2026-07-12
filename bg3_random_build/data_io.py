import csv
import os
from typing import Dict, FrozenSet, List, Set, Tuple

from .models import SubBreakpoint


ThemeRequirements = Dict[str, List[FrozenSet[str]]]


def _split_semicolon_values(raw: str) -> List[str]:
    return [value.strip() for value in raw.split(";") if value.strip()]


def load_breakpoints(path: str) -> List[SubBreakpoint]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Breakpoint file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext != ".csv":
        raise ValueError("Unsupported breakpoint file type. Use .csv")

    out: List[SubBreakpoint] = []
    seen_subclasses: Set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_columns = {"subclass", "levels", "parent_class", "capabilities"}
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Breakpoint CSV is missing columns: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            subclass = row["subclass"].strip()
            parent_class = row["parent_class"].strip()
            if not subclass or not parent_class:
                raise ValueError(f"Breakpoint CSV line {line_number} has an empty subclass or parent_class")
            if subclass in seen_subclasses:
                raise ValueError(
                    f"Breakpoint CSV line {line_number} repeats subclass '{subclass}'. "
                    "Put all valid levels in one semicolon-separated row."
                )
            seen_subclasses.add(subclass)

            raw_levels = _split_semicolon_values(row["levels"])
            if not raw_levels:
                raise ValueError(f"Breakpoint CSV line {line_number} has no levels")
            try:
                levels = [int(value) for value in raw_levels]
            except ValueError as exc:
                raise ValueError(f"Breakpoint CSV line {line_number} contains a non-integer level") from exc
            if any(level < 1 or level > 12 for level in levels):
                raise ValueError(f"Breakpoint CSV line {line_number} contains a level outside 1-12")
            if len(levels) != len(set(levels)):
                raise ValueError(f"Breakpoint CSV line {line_number} contains duplicate levels")

            capabilities = frozenset(_split_semicolon_values(row.get("capabilities") or ""))
            for level in levels:
                out.append(SubBreakpoint(subclass, level, parent_class, capabilities))

    return out


def load_themes(path: str) -> Tuple[Dict[str, str], ThemeRequirements]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Theme file not found: {path}")

    themes: Dict[str, str] = {}
    reqs: ThemeRequirements = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_columns = {"adjective", "blurb", "required_capabilities"}
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Theme CSV is missing columns: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            adjective = row["adjective"].strip()
            if not adjective:
                raise ValueError(f"Theme CSV line {line_number} has an empty adjective")
            if adjective in themes:
                raise ValueError(f"Theme CSV line {line_number} repeats adjective '{adjective}'")

            themes[adjective] = row["blurb"].strip()
            raw = (row.get("required_capabilities") or "").strip()
            if raw:
                alternatives: List[FrozenSet[str]] = []
                for alternative in _split_semicolon_values(raw):
                    required = frozenset(part.strip() for part in alternative.split("+") if part.strip())
                    if not required:
                        raise ValueError(
                            f"Theme CSV line {line_number} has an empty capability requirement"
                        )
                    alternatives.append(required)
                reqs[adjective] = alternatives

    return themes, reqs
