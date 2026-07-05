import pathlib

import streamlit as st

from bg3_random_build.config import DEFAULTS
from bg3_random_build.data_io import load_breakpoints, load_themes
from bg3_random_build.logic import suggest_many


HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_BREAKPOINTS = HERE / DEFAULTS.breakpoints_path
DEFAULT_THEMES = HERE / DEFAULTS.themes_path

st.set_page_config(page_title="BG3 Random Build Generator", page_icon="", layout="centered")
st.title("BG3 Random Build Generator")
st.caption("Generate random, probably silly, BG3 build suggestions. See it as a challenge ;)")

n = st.number_input("Number of builds", min_value=1, max_value=20, value=4, step=1)
include_theme = st.checkbox(
    'Include build "theme" (might be silly)',
    value=True,
    help="When off, only suggest class levels and simple names.",
)

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

subclasses_by_parent = {}
for bp in sub_bps:
    subclasses_by_parent.setdefault(bp.parent_class, set()).add(bp.subclass)

with st.expander("Subclass pool", expanded=False):
    st.caption("Choose which subclasses are allowed to appear. Default is all.")

    selected_subclasses = set()
    for parent in sorted(subclasses_by_parent):
        options = sorted(subclasses_by_parent[parent])
        selected = st.multiselect(
            parent,
            options=options,
            default=options,
            key=f"subclass_pool_{parent}",
        )
        selected_subclasses.update(selected)

filtered_sub_bps = [bp for bp in sub_bps if bp.subclass in selected_subclasses]

if not filtered_sub_bps:
    st.warning("Pick at least one subclass to generate builds.")
    st.stop()

if st.button("Generate"):
    try:
        builds = suggest_many(
            filtered_sub_bps,
            themes,
            theme_reqs,
            n=int(n),
            use_adjective=include_theme,
            include_blurb=include_theme,
        )
    except RuntimeError as e:
        st.error(f"Could not generate a valid build from the selected subclass pool: {e}")
        st.stop()

    for name, line in builds:
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(line)
