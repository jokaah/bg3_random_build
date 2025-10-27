import argparse, sys, random
from .config import DEFAULTS
from .data_io import load_breakpoints, load_themes
from .logic import suggest_many

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bg3-builds",
        description="Generate themed BG3 multiclass builds from breakpoint CSVs."
    )
    p.add_argument("-n", "--num", type=int, default=4, help="How many builds to generate.")
    p.add_argument("--breakpoints", default=DEFAULTS.breakpoints_path, help="Path to breakpoints CSV.")
    p.add_argument("--themes", default=DEFAULTS.themes_path, help="Path to themes CSV.")
    p.add_argument("--level-cap", type=int, default=DEFAULTS.level_cap, help="Level cap.")
    p.add_argument("--show-parent-in-label", action="store_true", help="Show parent class in label.")
    p.add_argument("--no-ea-if-martial", dest="ea_if_martial", action="store_false", help="Do not require Extra Attack for pure martial comps.")
    p.add_argument("--prefer-ea-if-hybrid", type=float, default=DEFAULTS.prefer_ea_if_hybrid, help="Probability to prefer EA for hybrid comps (0-1).")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    return p

def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    try:
        sub_bps = load_breakpoints(args.breakpoints)
    except Exception as e:
        print(f"Error loading breakpoint file '{args.breakpoints}': {e}", file=sys.stderr)
        return 2

    try:
        themes, theme_reqs = load_themes(args.themes)
    except Exception as e:
        print(f"Error loading themes file '{args.themes}': {e}", file=sys.stderr)
        return 3

    builds = suggest_many(
        sub_bps,
        themes,
        theme_reqs,
        n=args.num,
        level_cap=args.level_cap,
        show_parent_in_label=args.show_parent_in_label,
        require_ea_if_martial=args.ea_if_martial,
        prefer_ea_if_hybrid=args.prefer_ea_if_hybrid,
    )
    for name, line in builds:
        print(name, line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())