from dataclasses import dataclass

@dataclass(frozen=True)
class Defaults:
    level_cap: int = 12
    num_subclasses_weights: dict = None
    show_parent_in_label: bool = False
    require_ea_if_martial: bool = True
    prefer_ea_if_hybrid: float = 0.7
    breakpoints_path: str = "breakpoints.csv"
    themes_path: str = "themes.csv"
    name_max_hooks: int = 1
    use_adjective: bool = True

DEFAULTS = Defaults(
    level_cap=12,
    num_subclasses_weights={1: 0.05, 2: 0.45, 3: 0.40, 4: 0.10},
    show_parent_in_label=False,
    require_ea_if_martial=True,
    prefer_ea_if_hybrid=0.7,
    breakpoints_path="breakpoints.csv",
    themes_path="themes.csv",
    name_max_hooks=1,
    use_adjective=True,
)

# Role groupings and thresholds are fairly static; keep here.
MARTIAL_PARENTS = {"Barbarian", "Fighter", "Paladin", "Ranger", "Rogue", "Monk"}
CASTER_PARENTS = {"Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard"}

EA_PARENT_THRESHOLDS = {"Barbarian": 5, "Fighter": 5, "Paladin": 5, "Ranger": 5, "Monk": 5}
EA_SUBCLASS_THRESHOLDS = {("Bard", "Valour"): 6, ("Bard", "Sword"): 6, ("Wizard", "Bladesinging"): 6}

ROLE_SUFFIX_BY_PARENT = {
    "Barbarian": ["Berserker", "Bruiser", "Ravager", "Warchief"],
    "Bard": ["Skald", "Virtuoso", "Bard", "War Bard"],
    "Cleric": ["Cleric", "Templar", "Chaplain", "Battle Cleric"],
    "Druid": ["Druid", "Warden", "Shapecaller", "Wild Shaper"],
    "Fighter": ["Fighter", "Vanguard", "Blademaster", "Weapon Master"],
    "Monk": ["Monk", "Adept", "Hand", "Fist"],
    "Paladin": ["Paladin", "Templar", "Crusader", "Justicar"],
    "Ranger": ["Ranger", "Stalker", "Pathfinder", "Skirmisher"],
    "Rogue": ["Trickster", "Skirmisher", "Cutpurse", "Duelist"],
    "Sorcerer": ["Sorcerer", "War Mage", "Bloodmage", "Stormcaller"],
    "Warlock": ["Warlock", "Hexblade", "Binder", "Pactblade"],
    "Wizard": ["Wizard", "Arcanist", "Evoker", "Magister"],
}

SECONDARY_SUFFIX_BY_COMP = {
    "martial": ["Skirmisher", "Slayer", "Marauder", "Vanguard"],
    "caster": ["Arcanist", "Invoker", "Spellweaver"],
    "hybrid": ["Spellblade", "Battlemage", "Magus"],
}

# Flavor hooks for optional name spice.
FLAVOR_MAP = {
    "Rogue": ["Shadow", "Knave", "Phantom", "Veil", "Skulk"],
    "Paladin": ["Oath", "Vow", "Sanctum", "Aegis", "Pledge"],
    "Fighter": ["Steel", "Surge", "Blade", "Guard", "Grit"],
    "Wizard": ["Sigil", "Glyph", "Weave", "Rune", "Cantrip"],
    "Warlock": ["Pact", "Whisper", "Hex", "Bind", "Boon"],
    "Sorcerer": ["Storm", "Spark", "Blood", "Flux", "Pulse"],
    "Barbarian": ["Rage", "Totem", "Frenzy", "Fury", "Howl"],
    "Monk": ["Palm", "Focus", "Step", "Form", "Flurry"],
    "Ranger": ["Stalker", "Trail", "Arrow", "Mark", "Hunt"],
    "Cleric": ["Prayer", "Light", "Ward", "Chalice", "Hallow"],
    "Druid": ["Circle", "Root", "Wilds", "Thorn", "Grove"],
    "Bard": ["Verse", "Muse", "Chord", "Refrain", "Ballad"],
}