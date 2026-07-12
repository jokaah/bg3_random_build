from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class SubBreakpoint:
    subclass: str
    levels: int
    parent_class: str
    capabilities: FrozenSet[str] = frozenset()

    def label(self, final_levels: int, show_parent: bool) -> str:
        if show_parent:
            return f"{self.parent_class} ({self.subclass}) {final_levels}"

        return f"{self.subclass} {final_levels}"
