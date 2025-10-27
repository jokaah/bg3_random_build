import pathlib
import random
import streamlit as st

from bg3_random_build.config import DEFAULTS
from bg3_random_build.data_io import load_breakpoints, load_themes
from bg3_random_build.logic import suggest_many

# Resolve data paths relative to this file location
HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_BREAKPOINTS = HERE / DEFAULTS.breakpoints_path
DEFAULT_THEMES = HERE / DEFAULTS.themes_path

st.set_page_config(page_title="BG3 Random Build Generator", page_icon="🎲", layout="centered")

st.title("🎲 BG3 Random Build Generator")
st.caption("Generate random, probably silly, BG3 build suggestions. See it as a challenge ;)")

# Single parameter as requested
n = st.number_input("Number of builds", min_value=1, max_value=20, value=4, step=1)

with st.sidebar:
    st.subheader("Data files")
    st.markdown(f"- **breakpoints:** `{DEFAULT_BREAKPOINTS.name}`")
    st.markdown(f"- **themes:** `{DEFAULT_THEMES.name}`")
    st.caption("Place custom CSVs next to this app and adapt code if needed.")

# Data loading
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

# Action
if st.button("Generate"):
    # optional seed? not exposed as a parameter, but keep possibility for reproducibility if needed
    builds = suggest_many(sub_bps, themes, theme_reqs, n=int(n))
    for idx, (name, line) in enumerate(builds, 1):
        with st.container(border=True):
            st.markdown(f"### {idx}. {name}")
            st.write(line)
