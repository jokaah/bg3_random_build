# BG3 Random Build Generator

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

## CSV format

`breakpoints.csv` stores one row per subclass. Put all valid breakpoint levels in the
`levels` column separated by semicolons. Capabilities are also semicolon-separated.
The generator chooses a subclass first and a valid breakpoint second, so subclasses
with more breakpoint options are not made more likely by those extra options.

`themes.csv` uses `required_capabilities`. Semicolons separate alternative requirements
(OR), while plus signs combine capabilities that must all be present (AND). For example,
`fire+martial;wildshape` accepts either a build with both `fire` and `martial`, or a
build with `wildshape`.
