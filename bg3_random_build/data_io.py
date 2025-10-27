import csv
import os
from typing import List, Dict, Tuple, Set

from .models import SubBreakpoint


def load_breakpoints(path: str) -> List[SubBreakpoint]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Breakpoint file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext != ".csv":
        raise ValueError("Unsupported breakpoint file type. Use .csv")

    out: List[SubBreakpoint] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append(SubBreakpoint(row["subclass"], int(row["levels"]), row["parent_class"]))

    return out


def load_themes(path: str) -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Theme file not found: {path}")

    themes: Dict[str, str] = {}
    reqs: Dict[str, Set[str]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            adj = row["adjective"].strip()
            blurb = row["blurb"].strip()
            themes[adj] = blurb
            raw = (row.get("requirements") or "").strip()
            if raw:
                reqs[adj] = {s.strip() for s in raw.split(";") if s.strip()}

    return themes, reqs
