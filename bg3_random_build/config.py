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


DEFAULTS = Defaults(num_subclasses_weights={1: 0.05, 2: 0.45, 3: 0.40, 4: 0.10})

MARTIAL_PARENTS = {"Barbarian", "Fighter", "Paladin", "Ranger", "Rogue", "Monk"}
CASTER_PARENTS = {"Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Artificer"}

EA_PARENT_THRESHOLDS = {
    "Barbarian": 5,
    "Fighter": 5,
    "Paladin": 5,
    "Ranger": 5,
    "Monk": 5,
}

EA_SUBCLASS_THRESHOLDS = {
    ("Bard", "Valour"): 6,
    ("Bard", "Sword"): 6,
    ("Wizard", "Bladesinging"): 6,
    ("Artificer", "Armorer"): 5,
    ("Artificer", "Battle Smith"): 5,
}

ROLE_SUFFIX_BY_PARENT = {
    "Barbarian": ["Ravager", "Berserker", "Reaver", "Wildheart", "Mauler", "Breaker"],
    "Bard": ["Virtuoso", "Skald", "Minstrel", "Troubadour", "Duelist", "Muse"],
    "Cleric": ["Oracle", "Templar", "Hierophant", "Exorcist", "Chaplain", "Lightbearer"],
    "Druid": ["Warden", "Shapecaller", "Thornspeaker", "Wildkeeper", "Groveguard", "Seer"],
    "Fighter": ["Vanguard", "Blademaster", "Weaponmaster", "Dreadnought", "Sentinel", "Bulwark"],
    "Monk": ["Adept", "Ascetic", "Fist", "Pilgrim", "Wayfarer", "Striker"],
    "Paladin": ["Justicar", "Crusader", "Oathkeeper", "Templar", "Avenger", "Warden"],
    "Ranger": ["Pathfinder", "Stalker", "Waywatcher", "Strider", "Tracker", "Skirmisher"],
    "Rogue": ["Knave", "Duelist", "Cutthroat", "Infiltrator", "Shade", "Trickster"],
    "Sorcerer": ["Stormcaller", "Spellblood", "Wildmage", "Arcanist", "Channeler", "Scion"],
    "Warlock": ["Hexbinder", "Pactblade", "Occultist", "Binder", "Doomspeaker", "Invoker"],
    "Wizard": ["Magister", "Arcanist", "Spellwright", "Runesage", "Evoker", "Savant"],
    "Artificer": ["Inventor", "Machinist", "Spellsmith", "Tinkerer", "Arcanotech", "Engineer"],
}

SECONDARY_SUFFIX_BY_COMP = {
    "martial": ["Slayer", "Vanguard", "Skirmisher", "Marauder", "Sentinel", "Duelist"],
    "caster": ["Invoker", "Spellweaver", "Arcanist", "Mystic", "Savant", "Channeler"],
    "hybrid": ["Spellblade", "Battlemage", "Magus", "Wardancer", "Hexblade", "Spellbreaker"],
}

FLAVOR_MAP = {
    "Barbarian": ["Rage", "Fury", "Howl", "Blood", "Fang", "Storm"],
    "Bard": ["Verse", "Chord", "Muse", "Encore", "Ballad", "Lute"],
    "Cleric": ["Prayer", "Dawn", "Hallow", "Reliquary", "Censer", "Ward"],
    "Druid": ["Thorn", "Root", "Grove", "Moon", "Wilds", "Briar"],
    "Fighter": ["Steel", "Blade", "Grit", "Banner", "Gauntlet", "Bulwark"],
    "Monk": ["Palm", "Flurry", "Focus", "Mantra", "Lotus", "Step"],
    "Paladin": ["Oath", "Vow", "Aegis", "Radiance", "Pledge", "Crown"],
    "Ranger": ["Trail", "Arrow", "Mark", "Hunt", "Fletching", "Talon"],
    "Rogue": ["Shadow", "Dagger", "Veil", "Cloak", "Silk", "Lockpick"],
    "Sorcerer": ["Spark", "Tempest", "Pulse", "Bloodline", "Surge", "Ember"],
    "Warlock": ["Pact", "Hex", "Whisper", "Bargain", "Eldritch", "Gloam"],
    "Wizard": ["Rune", "Glyph", "Sigil", "Weave", "Grimoire", "Ward"],
    "Artificer": ["Gear", "Gadget", "Aether", "Turret", "Elixir", "Runeplate"],
}
