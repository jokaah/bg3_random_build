# BG3 Random Build Generator (Refactor)

Clean, modular refactor with argparse and CSV-driven themes.

## Files
- `bg3_random_build/` package:
  - `config.py`: defaults and constants
  - `models.py`: dataclasses
  - `data_io.py`: CSV loaders
  - `logic.py`: core build logic (unchanged in behavior; tidied)
  - `cli.py`: argparse-based CLI
- `run_builds.py`: handy Python entrypoint
- `themes.csv`: adjectives + blurbs + requirements
- (Use your existing `breakpoints.csv`)

## Usage
```bash
python run_builds.py -n 5 --breakpoints breakpoints.csv --themes themes.csv
```

Optional flags:
- `--level-cap 12`
- `--show-parent-in-label`
- `--no-ea-if-martial`
- `--prefer-ea-if-hybrid 0.7`
- `--seed 42`

## CSV Schema

`themes.csv` columns:
- `adjective`: e.g., `Ashen`
- `blurb`: short thematic description
- `requirements`: semicolon-separated parent classes required for that adjective (leave empty if none)

Example:
```csv
adjective,blurb,requirements
Ashen,fire-themed brawler or phoenix rebirth vibe,Sorcerer;Warlock;Wizard
Ironbound,unyielding defensive frontline,Fighter;Barbarian;Paladin
```