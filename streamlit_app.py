import pathlib
from collections import OrderedDict

import streamlit as st

from bg3_random_build.config import DEFAULTS
from bg3_random_build.data_io import load_breakpoints, load_themes
from bg3_random_build.logic import suggest_many


HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_BREAKPOINTS = HERE / DEFAULTS.breakpoints_path
DEFAULT_THEMES = HERE / DEFAULTS.themes_path
DEFAULT_COMPOSITION_WEIGHTS = getattr(
    DEFAULTS,
    "composition_weights",
    None,
) or {"martial": 0.25, "caster": 0.35, "hybrid": 0.40}


@st.cache_data
def _load_breakpoints(path: str):
    return load_breakpoints(path)


@st.cache_data
def _load_themes(path: str):
    return load_themes(path)


def _subclasses_by_parent(sub_bps):
    grouped = OrderedDict()
    for bp in sub_bps:
        grouped.setdefault(bp.parent_class, [])
        if bp.subclass not in grouped[bp.parent_class]:
            grouped[bp.parent_class].append(bp.subclass)
    return grouped


st.set_page_config(page_title="BG3 Random Build Generator", page_icon="", layout="centered")
st.title(" BG3 Random Build Generator")
st.caption("Generate random, probably silly, BG3 build suggestions.\nSee it as a challenge ;)")

err = None
try:
    sub_bps_all = _load_breakpoints(str(DEFAULT_BREAKPOINTS))
except Exception as e:
    sub_bps_all = []
    err = f"Error loading breakpoints: {e}"

try:
    themes, theme_reqs = _load_themes(str(DEFAULT_THEMES))
except Exception as e:
    themes, theme_reqs = {}, {}
    err = f"Error loading themes: {e}" if not err else err + f" | {e}"

if err:
    st.error(err)
    st.stop()

n = st.number_input("Number of builds", min_value=1, max_value=20, value=4, step=1)
include_theme = st.checkbox(
    "Include build \"theme\" (might be silly)",
    value=True,
    help="When off, only suggest class levels and simple names.",
)

with st.expander("Subclass picker"):
    st.caption(
        "Choose which subclasses are allowed in the generator. "
        "Leave a class empty to exclude that parent class entirely."
    )
    grouped = _subclasses_by_parent(sub_bps_all)
    selected_subclasses = set()
    for parent, subclasses in grouped.items():
        selected = st.multiselect(
            parent,
            options=subclasses,
            default=subclasses,
            key=f"subclasses_{parent}",
        )
        selected_subclasses.update(selected)

with st.expander("Advanced composition weights"):
    st.caption(
        "These weights decide whether the chosen parent classes should be martial-only, "
        "caster-only, or a true martial/caster hybrid. They do not need to add up to 1."
    )
    martial_weight = st.number_input(
        "Martial-only weight",
        min_value=0.0,
        value=float(DEFAULT_COMPOSITION_WEIGHTS["martial"]),
        step=0.05,
    )
    caster_weight = st.number_input(
        "Caster-only weight",
        min_value=0.0,
        value=float(DEFAULT_COMPOSITION_WEIGHTS["caster"]),
        step=0.05,
    )
    hybrid_weight = st.number_input(
        "Hybrid weight",
        min_value=0.0,
        value=float(DEFAULT_COMPOSITION_WEIGHTS["hybrid"]),
        step=0.05,
    )

composition_weights = {
    "martial": martial_weight,
    "caster": caster_weight,
    "hybrid": hybrid_weight,
}

sub_bps = [bp for bp in sub_bps_all if bp.subclass in selected_subclasses]

if not sub_bps:
    st.error("Select at least one subclass before generating builds.")
    st.stop()

if sum(composition_weights.values()) <= 0:
    st.error("At least one composition weight must be greater than zero.")
    st.stop()

if st.button("Generate"):
    try:
        builds = suggest_many(
            sub_bps,
            themes,
            theme_reqs,
            n=int(n),
            composition_weights=composition_weights,
            use_adjective=include_theme,
            include_blurb=include_theme,
        )
    except Exception as e:
        st.error(f"Could not generate builds with the current settings: {e}")
        st.stop()

    for name, line in builds:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(line)
