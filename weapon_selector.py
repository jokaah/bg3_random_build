import argparse
import random
from pathlib import Path

import pandas as pd


WEAPONS_FILE = Path("weapons.csv")
SPELLS_FILE = Path("spells.csv")

PARTY_SIZE = 4

MONK_SUBCLASSES = [
    "Way of the Open Hand",
    "Way of Shadow",
    "Way of the Four Elements",
    "Way of the Drunken Master"
]


def is_yes(value):
    """Treat 'yes' as True and blanks/NaN as False."""
    if pd.isna(value):
        return False

    return str(value).strip().lower() == "yes"


def clean_optional(value):
    """Convert blank/NaN CSV values to None."""
    if pd.isna(value):
        return None

    value = str(value).strip()
    return value if value else None


def load_data():
    weapons = pd.read_csv(WEAPONS_FILE)
    spells = pd.read_csv(SPELLS_FILE)

    required_weapon_columns = {
        "item_name",
        "dual_wield_option",
        "generic_caster_staff",
        "monk_gloves",
        "early_replacement",
    }

    missing = required_weapon_columns - set(weapons.columns)

    if missing:
        raise ValueError(
            f"{WEAPONS_FILE} is missing columns: {', '.join(sorted(missing))}"
        )

    if "spell_name" not in spells.columns:
        raise ValueError(
            f"{SPELLS_FILE} must contain a 'spell_name' column."
        )

    return weapons, spells


def get_extra_rules(weapon_row, available_spells):
    """
    Roll/display any additional rules attached to a weapon:
    - main spell for generic caster staves
    - monk subclass for monk gloves
    - early replacement if specified
    """
    extras = {}

    if is_yes(weapon_row["generic_caster_staff"]):
        if not available_spells:
            raise RuntimeError("No spells remaining to assign.")

        spell = random.choice(available_spells)
        extras["main_spell"] = str(spell)
        available_spells.remove(spell)

    if is_yes(weapon_row["monk_gloves"]):
        extras["monk_subclass"] = random.choice(MONK_SUBCLASSES)

    replacement = clean_optional(weapon_row["early_replacement"])

    if replacement:
        extras["early_replacement"] = replacement

    return extras


def select_run(weapons, spells):
    # Work with dataframe indexes so every entry can only be selected once.
    remaining = set(weapons.index)

    # Spells are unique within this run.
    available_spells = spells["spell_name"].dropna().astype(str).tolist()

    selections = []

    # ---------------------------
    # 1. Select four primaries
    # ---------------------------
    primary_indexes = random.sample(
        list(remaining),
        k=PARTY_SIZE,
    )

    for index in primary_indexes:
        remaining.remove(index)

    # ---------------------------
    # 2. Build each character slot
    # ---------------------------
    for slot_number, primary_index in enumerate(primary_indexes, start=1):
        primary = weapons.loc[primary_index]

        selection = {
            "slot": slot_number,
            "primary": primary["item_name"],
            "primary_extras": get_extra_rules(
                primary,
                available_spells,
            ),
            "dual_wield_partner": None,
            "partner_extras": None,
        }

        # -----------------------------------------
        # Immediately reserve a dual-wield partner
        # -----------------------------------------
        if is_yes(primary["dual_wield_option"]):
            valid_partner_indexes = [
                index
                for index in remaining
                if is_yes(weapons.loc[index, "dual_wield_option"])
            ]

            if valid_partner_indexes:
                partner_index = random.choice(valid_partner_indexes)
                remaining.remove(partner_index)

                partner = weapons.loc[partner_index]

                selection["dual_wield_partner"] = partner["item_name"]
                selection["partner_extras"] = get_extra_rules(
                    partner,
                    available_spells,
                )

        selections.append(selection)

    return selections


def get_extras(extras) -> str:
    extras_str = ""

    if not extras:
        return extras_str


    if "main_spell" in extras:
        extras_str += f", Main spell: {extras['main_spell']}"

    if "monk_subclass" in extras:
        extras_str += f", Monk subclass: {extras['monk_subclass']}"

    if "early_replacement" in extras:
        extras_str += f", Use until obtained: {extras['early_replacement']}"
    
    return extras_str


def print_run(selections):
    for selection in selections:
        partner = selection["dual_wield_partner"]
        partner = f" (+ {partner})" if partner else ""
        extras = get_extras(selection["primary_extras"])
        partner_extras = get_extras(selection["partner_extras"])

        print(f"{selection['slot']}: {selection['primary']}{partner}{extras}{partner_extras}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a BG3 random weapon challenge run."
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed for reproducible rolls.",
    )

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    weapons, spells = load_data()

    if len(weapons) < PARTY_SIZE:
        raise RuntimeError(
            f"Need at least {PARTY_SIZE} weapons."
        )

    selections = select_run(weapons, spells)
    print_run(selections)


if __name__ == "__main__":
    main()