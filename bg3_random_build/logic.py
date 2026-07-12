import random
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from .config import (
    CASTER_PARENTS,
    DEFAULTS,
    EA_PARENT_THRESHOLDS,
    EA_SUBCLASS_THRESHOLDS,
    FLAVOR_MAP,
    MARTIAL_PARENTS,
    ROLE_SUFFIX_BY_PARENT,
    SECONDARY_SUFFIX_BY_COMP,
)
from .data_io import ThemeRequirements
from .models import SubBreakpoint


COMPOSITION_WEIGHT_DEFAULTS = getattr(
    DEFAULTS,
    "composition_weights",
    None,
) or {"martial": 0.25, "caster": 0.35, "hybrid": 0.40}


def weighted_choice(weight_map: Dict[int, float]) -> int:
    vals, wts = zip(*weight_map.items())
    return random.choices(vals, weights=wts, k=1)[0]


def weighted_choice_str(weight_map: Dict[str, float]) -> str:
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


def choose_parents_for_composition(k: int, available_parents: List[str], comp_target: str) -> List[str]:
    """Choose parent classes for the requested broad composition.

    martial: only martial parents
    caster: only caster parents
    hybrid: at least one martial and one caster parent
    """
    martial = [p for p in available_parents if p in MARTIAL_PARENTS]
    caster = [p for p in available_parents if p in CASTER_PARENTS]

    if comp_target == "martial":
        return choose_k_parents(k, martial)

    if comp_target == "caster":
        return choose_k_parents(k, caster)

    if comp_target == "hybrid":
        if k < 2 or not martial or not caster:
            return []
        parents = [random.choice(martial), random.choice(caster)]
        remaining_pool = [p for p in available_parents if p not in parents]
        extra = choose_k_parents(k - 2, remaining_pool)
        if len(extra) != k - 2:
            return []
        parents.extend(extra)
        random.shuffle(parents)
        return parents

    return choose_k_parents(k, available_parents)


def choose_subclasses_for_composition(
    k: int,
    options_by_subclass: Dict[str, List[SubBreakpoint]],
    comp_target: str,
    max_tries: int = 2000,
) -> List[str]:
    """Choose subclasses directly so breakpoint count cannot affect selection weight.

    A valid build may use at most one subclass from each parent class. Composition
    constraints are checked after sampling, keeping subclasses within each eligible
    composition equally likely rather than choosing parent classes first.
    """
    subclasses = list(options_by_subclass)
    if k > len(subclasses):
        return []

    for _ in range(max_tries):
        chosen = random.sample(subclasses, k)
        parents = [options_by_subclass[subclass][0].parent_class for subclass in chosen]
        if len(set(parents)) != k:
            continue

        has_martial = any(parent in MARTIAL_PARENTS for parent in parents)
        has_caster = any(parent in CASTER_PARENTS for parent in parents)
        if comp_target == "martial" and not all(parent in MARTIAL_PARENTS for parent in parents):
            continue
        if comp_target == "caster" and not all(parent in CASTER_PARENTS for parent in parents):
            continue
        if comp_target == "hybrid" and (k < 2 or not has_martial or not has_caster):
            continue
        return chosen

    return []


def try_find_combo_for_subclasses(
    cap: int,
    chosen_subclasses: List[str],
    options_by_subclass: Dict[str, List[SubBreakpoint]],
    max_random_tries: int = 8000,
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
    want_ea: bool,
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


def _build_capabilities(picks: List[SubBreakpoint]) -> Set[str]:
    capabilities: Set[str] = set()
    for bp in picks:
        capabilities.update(bp.capabilities)
    return capabilities


def adjective_fits(
    adjective: str,
    build_capabilities: Set[str],
    theme_requirements: ThemeRequirements,
    has_martial_access: bool = True,
) -> bool:
    alternatives = theme_requirements.get(adjective)
    if not alternatives:
        return True

    # Current loaders return a list of frozensets. This small compatibility
    # guard also handles legacy in-memory values from the old web app schema.
    normalized = []
    if isinstance(alternatives, str):
        alternatives = [part.strip() for part in alternatives.split(";") if part.strip()]
    for required in alternatives:
        if isinstance(required, str):
            required = frozenset(
                part.strip() for part in required.split("+") if part.strip()
            )
        normalized.append(required)
    return any(
        required.issubset(build_capabilities)
        and ("martial" not in required or has_martial_access)
        for required in normalized
    )


def _has_martial_theme_access(
    final_levels: Dict[Tuple[str, str], int],
    picks: List[SubBreakpoint],
) -> bool:
    """Return whether the finished build may use martial-gated themes.

    Martial themes require either a Rogue level or a class/subclass that has
    actually reached its Extra Attack threshold. Merely carrying the martial
    capability tag is not enough.
    """
    has_rogue = any(
        parent == "Rogue" and level >= 4
        for (_, parent), level in final_levels.items()
    )
    return has_rogue or _has_extra_attack(final_levels, picks)


def pick_adjective_for(
    picks: List[SubBreakpoint],
    final_levels: Dict[Tuple[str, str], int],
    themes: Dict[str, str],
    theme_requirements: ThemeRequirements,
) -> str:
    build_capabilities = _build_capabilities(picks)
    has_martial_access = _has_martial_theme_access(final_levels, picks)
    fitting = [
        adjective
        for adjective in themes
        if adjective_fits(
            adjective,
            build_capabilities,
            theme_requirements,
            has_martial_access=has_martial_access,
        )
    ]
    if not fitting:
        raise RuntimeError(
            "No theme matches the selected subclasses' capabilities. "
            "Add an unrestricted theme or review the capability tags."
        )
    return random.choice(fitting)

def _levels_by_parent(final_levels: Dict[Tuple[str, str], int]) -> Dict[str, int]:
    by_parent: Dict[str, int] = {}
    for (_, parent), lvl in final_levels.items():
        by_parent[parent] = by_parent.get(parent, 0) + lvl
    return by_parent


def _dominant_parent(final_levels: Dict[Tuple[str, str], int]) -> str:
    by_parent = _levels_by_parent(final_levels)
    return max(by_parent.items(), key=lambda kv: kv[1])[0]


def _top_name_parents(final_levels: Dict[Tuple[str, str], int], limit: int = 2) -> List[str]:
    """Return the parent classes allowed to contribute flavor words to a build name."""
    by_parent = _levels_by_parent(final_levels)
    ranked = sorted(by_parent.items(), key=lambda kv: (-kv[1], kv[0]))
    return [parent for parent, _ in ranked[:limit]]


def _composition_role(final_levels: Dict[Tuple[str, str], int]) -> str:
    m = c = 0
    by_parent = _levels_by_parent(final_levels)
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


def build_name_and_blurb(
    picks: List[SubBreakpoint],
    final_levels: Dict[Tuple[str, str], int],
    themes: Dict[str, str],
    theme_requirements: ThemeRequirements,
    name_max_hooks: int,
    use_adjective: bool,
) -> Tuple[str, str]:
    comp = _composition_role(final_levels)
    dom = _dominant_parent(final_levels)
    adjective = pick_adjective_for(picks, final_levels, themes, theme_requirements)
    blurb = themes.get(adjective, "themed build")
    role1 = _pick_role_suffix(dom, comp)
    role2 = None
    if comp in SECONDARY_SUFFIX_BY_COMP and random.random() < 0.45:
        role2 = random.choice(SECONDARY_SUFFIX_BY_COMP[comp])
        if role2 == role1 and len(SECONDARY_SUFFIX_BY_COMP[comp]) > 1:
            role2 = random.choice([r for r in SECONDARY_SUFFIX_BY_COMP[comp] if r != role1])

    hooks = []
    if name_max_hooks > 0:
        # Avoid the old word-salad effect: only the top two parent classes by final
        # level investment are allowed to contribute flavor hooks to the name.
        for parent in _top_name_parents(final_levels, limit=2):
            if parent in FLAVOR_MAP and FLAVOR_MAP[parent]:
                hooks.append(random.choice(FLAVOR_MAP[parent]))
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


def format_build(
    picks: List[SubBreakpoint],
    final_levels: Dict[Tuple[str, str], int],
    blurb: str,
    show_parent_in_label: bool,
    include_blurb: bool = True,
) -> str:
    parts = []
    for bp in picks:
        key = (bp.subclass, bp.parent_class)
        parts.append(bp.label(final_levels[key], show_parent=show_parent_in_label))
    core = " / ".join(sorted(parts))
    return f"{core} ({blurb})" if include_blurb and blurb else core


def suggest_build(
    sub_bps: List[SubBreakpoint],
    themes: Dict[str, str],
    theme_requirements: ThemeRequirements,
    level_cap: int = DEFAULTS.level_cap,
    num_subclass_weights: Dict[int, float] = None,
    composition_weights: Dict[str, float] = None,
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
    if composition_weights is None:
        composition_weights = COMPOSITION_WEIGHT_DEFAULTS

    options_by_subclass, subclasses_by_parent = index_structures(sub_bps)
    available_parents = list(subclasses_by_parent.keys())
    if not available_parents:
        raise RuntimeError("No subclasses available.")

    for _ in range(max_global_attempts):
        k = weighted_choice(num_subclass_weights)
        if k > len(available_parents):
            continue

        comp_target = weighted_choice_str(composition_weights)
        for __ in range(80):
            chosen_subclasses = choose_subclasses_for_composition(
                k, options_by_subclass, comp_target
            )
            if not chosen_subclasses:
                continue
            picks = try_find_combo_for_subclasses(level_cap, chosen_subclasses, options_by_subclass)
            if not picks:
                continue

            prelim = fill_to_cap_with_preferences(picks, level_cap, want_ea=False)
            comp = _composition_role(prelim)
            want_ea = (comp == "martial" and require_ea_if_martial) or (
                comp == "hybrid" and random.random() < prefer_ea_if_hybrid
            )
            finals = fill_to_cap_with_preferences(picks, level_cap, want_ea=want_ea)
            if want_ea and not _has_extra_attack(finals, picks):
                continue

            name, blurb = build_name_and_blurb(
                picks,
                finals,
                themes,
                theme_requirements,
                name_max_hooks,
                use_adjective,
            )
            line = format_build(
                picks,
                finals,
                blurb,
                show_parent_in_label,
                include_blurb=include_blurb,
            )
            return name, line

    raise RuntimeError("No valid combination found.")


def suggest_many(
    sub_bps: List[SubBreakpoint],
    themes: Dict[str, str],
    theme_requirements: ThemeRequirements,
    n: int = 4,
    **kwargs,
) -> List[Tuple[str, str]]:
    out = []
    for _ in range(n):
        name, line = suggest_build(sub_bps, themes, theme_requirements, **kwargs)
        out.append((name, line))
    return out
