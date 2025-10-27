from dataclasses import dataclass


@dataclass(frozen=True)
class SubBreakpoint:
    subclass: str
    levels: int
    parent_class: str

    def label(self, final_levels: int, show_parent: bool) -> str:
        if show_parent:
            return f"{self.parent_class} ({self.subclass}) {final_levels}"

        return f"{self.subclass} {final_levels}"
