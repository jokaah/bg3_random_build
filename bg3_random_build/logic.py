import random
from typing import List, Dict, Tuple, Optional, Set
from .models import SubBreakpoint
from .config import (
    DEFAULTS, MARTIAL_PARENTS, CASTER_PARENTS,
    EA_PARENT_THRESHOLDS, EA_SUBCLASS_THRESHOLDS,
    ROLE_SUFFIX_BY_PARENT, SECONDARY_SUFFIX_BY_COMP, FLAVOR_MAP
)

def weighted_choice(weight_map: Dict[int, float]) -> int:
    vals, wts = zip(*weight_map.items())
    return random.choices(vals, weights=wts, k=1)[0]

def index_structures(sub_bps: List[SubBreakpoint]):
    options_by_subclass: Dict[str, List[SubBreakpoint]] = {}
    subclasses_by_parent: Dict[str, List[str]] = {}
    for bp in sub_bps:
        options_by_subclass.setdefault(bp.subclass, []).append(bp)
        if bp.subclass not in subclasses_by_parent.setdefault(bp.parent_class, []):
            subclasses_by_parent[bp.parent_class].append(bp.subclass)
    return options_by_subclass, subclasses_by_parent

def choose_k_parents(k: int, parents: List[str]) -> List[str]:
    if k > len(parents):
        return []
    return random.sample(parents, k)

def try_find_combo_for_subclasses(
        cap: int,
        chosen_subclasses: List[str],
        options_by_subclass: Dict[str, List[SubBreakpoint]],
        max_random_tries: int = 8000
) -> Optional[List[SubBreakpoint]]:
    if not chosen_subclasses:
        return None
    min_sum = sum(min(bp.levels for bp in options_by_subclass[s]) for s in chosen_subclasses)
    if min_sum > cap:
        return None
    for _ in range(max_random_tries):
        pick: List[SubBreakpoint] = []
        total = 0
        feasible = True
        for sc in chosen_subclasses:
            bp = random.choice(options_by_subclass[sc])
            pick.append(bp)
            total += bp.levels
            if total > cap:
                feasible = False
                break
        if feasible:
            return pick
    return None

def _ea_threshold_for(bp: SubBreakpoint) -> Optional[int]:
    if bp.parent_class in EA_PARENT_THRESHOLDS:
        return EA_PARENT_THRESHOLDS[bp.parent_class]
    return EA_SUBCLASS_THRESHOLDS.get((bp.parent_class, bp.subclass))

def _has_extra_attack(finals: Dict[Tuple[str, str], int], picks: List[SubBreakpoint]) -> bool:
    for bp in picks:
        key = (bp.subclass, bp.parent_class)
        th = _ea_threshold_for(bp)
        if th is not None and finals.get(key, 0) >= th:
            return True
    return False

def fill_to_cap_with_preferences(
        picks: List[SubBreakpoint],
        cap: int,
        want_ea: bool
) -> Dict[Tuple[str, str], int]:
    finals: Dict[Tuple[str, str], int] = {}
    for bp in picks:
        finals[(bp.subclass, bp.parent_class)] = finals.get((bp.subclass, bp.parent_class), 0) + bp.levels
    remaining = cap - sum(finals.values())
    if remaining <= 0:
        return finals
    keys = list(finals.keys())

    if want_ea and remaining > 0:
        candidates = []
        for bp in picks:
            key = (bp.subclass, bp.parent_class)
            th = _ea_threshold_for(bp)
            if th is None:
                continue
            cur = finals[key]
            if cur >= th:
                candidates = []
                break
            need = th - cur
            if need > 0:
                candidates.append((need, key, th))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            need, key, _ = candidates[0]
            alloc = min(need, remaining)
            finals[key] += alloc
            remaining -= alloc

    if remaining > 0:
        odd_keys = [k for k in keys if finals[k] % 2 == 1]
        random.shuffle(odd_keys)
        for k in odd_keys:
            if remaining == 0:
                break
            finals[k] += 1
            remaining -= 1

    while remaining >= 2:
        random.shuffle(keys)
        for k in keys:
            if remaining < 2:
                break
            finals[k] += 2
            remaining -= 2

    if remaining == 1:
        candidates = [k for k in keys if finals[k] % 2 == 1]
        if not candidates:
            candidates = keys[:]
        finals[random.choice(candidates)] += 1
    return finals

def _parents_in_build(final_levels: Dict[Tuple[str, str], int]) -> Set[str]:
    parents = set()
    for (_, parent), lvl in final_levels.items():
        if lvl > 0:
            parents.add(parent)
    return parents

def adjective_fits(adjective: str, final_levels: Dict[Tuple[str, str], int], theme_requirements: Dict[str, Set[str]]) -> bool:
    req = theme_requirements.get(adjective)
    if not req:
        return True
    return len(req & _parents_in_build(final_levels)) > 0

def pick_adjective_for(final_levels: Dict[Tuple[str, str], int], themes: Dict[str, str], theme_requirements: Dict[str, Set[str]]) -> str:
    fitting = [a for a in themes.keys() if adjective_fits(a, final_levels, theme_requirements)]
    if fitting:
        return random.choice(fitting)
    return random.choice(list(themes.keys()))

def _dominant_parent(final_levels: Dict[Tuple[str, str], int]) -> str:
    by_parent: Dict[str, int] = {}
    for (sub, parent), lvl in final_levels.items():
        by_parent[parent] = by_parent.get(parent, 0) + lvl
    return max(by_parent.items(), key=lambda kv: kv[1])[0]

def _composition_role(final_levels: Dict[Tuple[str, str], int]) -> str:
    m = c = 0
    by_parent: Dict[str, int] = {}
    for (sub, parent), lvl in final_levels.items():
        by_parent[parent] = by_parent.get(parent, 0) + lvl
    for parent, total in by_parent.items():
        if parent in MARTIAL_PARENTS:
            m += total
        if parent in CASTER_PARENTS:
            c += total
    if m > 0 and c > 0:
        return "hybrid"
    return "martial" if m >= c else "caster"

def _pick_role_suffix(dominant_parent: str, comp: str) -> str:
    if dominant_parent in ROLE_SUFFIX_BY_PARENT:
        return random.choice(ROLE_SUFFIX_BY_PARENT[dominant_parent])
    if comp == "hybrid":
        return random.choice(SECONDARY_SUFFIX_BY_COMP["hybrid"])
    if comp == "martial":
        return random.choice(["Fighter", "Vanguard", "Skirmisher"])
    return random.choice(["Caster", "Invoker", "Arcanist"])

def build_name_and_blurb(picks: List[SubBreakpoint],
                         final_levels: Dict[Tuple[str, str], int],
                         themes: Dict[str, str],
                         theme_requirements: Dict[str, set],
                         name_max_hooks: int,
                         use_adjective: bool) -> Tuple[str, str]:
    comp = _composition_role(final_levels)
    dom = _dominant_parent(final_levels)

    adjective = pick_adjective_for(final_levels, themes, theme_requirements)
    blurb = themes.get(adjective, "themed build")

    role1 = _pick_role_suffix(dom, comp)
    role2 = None
    if comp in SECONDARY_SUFFIX_BY_COMP and random.random() < 0.45:
        role2 = random.choice(SECONDARY_SUFFIX_BY_COMP[comp])
        if role2 == role1 and len(SECONDARY_SUFFIX_BY_COMP[comp]) > 1:
            role2 = random.choice([r for r in SECONDARY_SUFFIX_BY_COMP[comp] if r != role1])

    hooks = []
    if name_max_hooks > 0:
        parents = [bp.parent_class for bp in picks]
        for p in parents:
            if p in FLAVOR_MAP and FLAVOR_MAP[p]:
                hooks.append(random.choice(FLAVOR_MAP[p]))
        random.shuffle(hooks)
        hooks = hooks[:name_max_hooks]

    parts = []
    if use_adjective:
        parts.append(adjective)
    parts += hooks
    parts.append(role1)
    if role2:
        parts.append(role2)

    return " ".join(parts), blurb

def format_build(picks: List[SubBreakpoint], final_levels: Dict[Tuple[str, str], int], blurb: str, show_parent_in_label: bool, include_blurb: bool = True) -> str:
    parts = []
    for bp in picks:
        key = (bp.subclass, bp.parent_class)
        parts.append(bp.label(final_levels[key], show_parent=show_parent_in_label))
    core = ' / '.join(sorted(parts))
    return f"{core} ({blurb})" if include_blurb and blurb else core

def suggest_build(
        sub_bps: List[SubBreakpoint],
        themes: Dict[str, str],
        theme_requirements: Dict[str, set],
        level_cap: int = DEFAULTS.level_cap,
        num_subclass_weights: Dict[int, float] = None,
        max_global_attempts: int = 800,
        show_parent_in_label: bool = DEFAULTS.show_parent_in_label,
        require_ea_if_martial: bool = DEFAULTS.require_ea_if_martial,
        prefer_ea_if_hybrid: float = DEFAULTS.prefer_ea_if_hybrid,
        name_max_hooks: int = DEFAULTS.name_max_hooks,
        use_adjective: bool = DEFAULTS.use_adjective,
        include_blurb: bool = True,
) -> Tuple[str, str]:
    if num_subclass_weights is None:
        num_subclass_weights = DEFAULTS.num_subclasses_weights

    options_by_subclass, subclasses_by_parent = index_structures(sub_bps)
    available_parents = list(subclasses_by_parent.keys())
    if not available_parents:
        raise RuntimeError("No subclasses available.")

    for _ in range(max_global_attempts):
        k = weighted_choice(num_subclass_weights)
        if k > len(available_parents):
            continue
        parents = choose_k_parents(k, available_parents)
        if not parents:
            continue

        for __ in range(80):
            chosen_subclasses = [random.choice(subclasses_by_parent[p]) for p in parents]
            picks = try_find_combo_for_subclasses(level_cap, chosen_subclasses, options_by_subclass)
            if not picks:
                continue

            prelim = fill_to_cap_with_preferences(picks, level_cap, want_ea=False)
            comp = _composition_role(prelim)
            want_ea = (comp == "martial" and require_ea_if_martial) or (comp == "hybrid" and random.random() < prefer_ea_if_hybrid)

            finals = fill_to_cap_with_preferences(picks, level_cap, want_ea=want_ea)
            if want_ea and not _has_extra_attack(finals, picks):
                continue

            name, blurb = build_name_and_blurb(picks, finals, themes, theme_requirements, name_max_hooks, use_adjective)
            line = format_build(picks, finals, blurb, show_parent_in_label, include_blurb=include_blurb)
            return (name + ":", line)

    raise RuntimeError("No valid combination found. Consider adding lower-level breakpoints or allowing fewer subclasses.")

def suggest_many(sub_bps: List[SubBreakpoint], themes: Dict[str, str], theme_requirements: Dict[str, set], n: int = 5, **kwargs) -> List[Tuple[str, str]]:
    out = []
    for _ in range(n):
        name, line = suggest_build(sub_bps, themes, theme_requirements, **kwargs)
        out.append((name, line))
    return out