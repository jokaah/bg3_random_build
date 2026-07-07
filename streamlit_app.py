import pathlib

import streamlit as st

from bg3_random_build.config import DEFAULTS
from bg3_random_build.data_io import load_breakpoints, load_themes
from bg3_random_build.logic import suggest_many


HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_BREAKPOINTS = HERE / DEFAULTS.breakpoints_path
DEFAULT_THEMES = HERE / DEFAULTS.themes_path

st.set_page_config(page_title="BG3 Random Build Generator", page_icon="", layout="centered")
st.title(" BG3 Random Build Generator")
st.caption("Generate random, probably silly, BG3 build suggestions.\nSee it as a challenge ;)")

n = st.number_input("Number of builds", min_value=1, max_value=20, value=4, step=1)
include_theme = st.checkbox(
    "Include build \"theme\" (might be silly)",
    value=True,
    help="When off, only suggest class levels and simple names.",
)

with st.expander("Advanced composition weights"):
    st.caption(
        "These weights decide whether the chosen parent classes should be martial-only, "
        "caster-only, or a true martial/caster hybrid. They do not need to add up to 1."
    )
    martial_weight = st.number_input(
        "Martial-only weight",
        min_value=0.0,
        value=float(DEFAULTS.composition_weights["martial"]),
        step=0.05,
    )
    caster_weight = st.number_input(
        "Caster-only weight",
        min_value=0.0,
        value=float(DEFAULTS.composition_weights["caster"]),
        step=0.05,
    )
    hybrid_weight = st.number_input(
        "Hybrid weight",
        min_value=0.0,
        value=float(DEFAULTS.composition_weights["hybrid"]),
        step=0.05,
    )

composition_weights = {
    "martial": martial_weight,
    "caster": caster_weight,
    "hybrid": hybrid_weight,
}

err = None
try:
    sub_bps = load_breakpoints(str(DEFAULT_BREAKPOINTS))
except Exception as e:
    err = f"Error loading breakpoints: {e}"

try:
    themes, theme_reqs = load_themes(str(DEFAULT_THEMES))
except Exception as e:
    err = f"Error loading themes: {e}" if not err else err + f" | {e}"

if err:
    st.error(err)
    st.stop()

if sum(composition_weights.values()) <= 0:
    st.error("At least one composition weight must be greater than zero.")
    st.stop()

if st.button("Generate"):
    for name, line in suggest_many(
        sub_bps,
        themes,
        theme_reqs,
        n=int(n),
        composition_weights=composition_weights,
        use_adjective=include_theme,
        include_blurb=include_theme,
    ):
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(line)
