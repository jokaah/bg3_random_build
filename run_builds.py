# Convenience entrypoint so you can run:
#   python run_builds.py -n 5 --breakpoints breakpoints.csv --themes themes.csv
from bg3_random_build.cli import main

if __name__ == "__main__":
    raise SystemExit(main())