import pathlib

import streamlit as st

from bg3_random_build.config import DEFAULTS
from bg3_random_build.data_io import load_breakpoints, load_themes
from bg3_random_build.logic import suggest_many

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_BREAKPOINTS = HERE / DEFAULTS.breakpoints_path
DEFAULT_THEMES = HERE / DEFAULTS.themes_path

st.set_page_config(page_title="BG3 Random Build Generator", page_icon="🎲", layout="centered")

st.title("🎲 BG3 Random Build Generator")
st.caption("Generate random, probably silly, BG3 build suggestions. See it as a challenge ;)")

n = st.number_input("Number of builds", min_value=1, max_value=20, value=4, step=1)

include_theme = st.checkbox(
    "Include build \"theme\" (might be silly)",
    value=True,
    help="When off, only suggest class levels and simple names."
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

if st.button("Generate"):
    for name, line in suggest_many(sub_bps, themes, theme_reqs, n=int(n), use_adjective=include_theme, include_blurb=include_theme):
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.write(line)
