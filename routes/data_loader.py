# routes/data_loader.py

ARTEFACT_MAIN_STATS = {
    "Casque": ["ATK", "ATK%", "DEF", "DEF%", "HP", "HP%"],
    "Plastron": ["DEF", "DEF%"],
    "Gants": ["ATK", "ATK%"],
    "Bottes": ["CRIT DMG", "DEF", "DEF%", "HP", "HP%"],
    "Collier": ["HP", "HP%"],
    "Bracelet": ["LIGHT DMG", "WATER DMG", "FIRE DMG", "WIND DMG", "DARK DMG"],
    "Bague": ["ATK", "ATK%", "DEF", "DEF%", "HP", "HP%"],
    "Boucle d'oreille": ["MP MAX"],
    "Helmet": ["ATK", "ATK%", "DEF", "DEF%", "HP", "HP%"],
    "Chestplate": ["DEF", "DEF%"],
    "Gloves": ["ATK", "ATK%"],
    "Boots": ["CRIT DMG", "DEF", "DEF%", "HP", "HP%"],
    "Necklace": ["HP", "HP%"],
    "Ring": ["ATK", "ATK%", "DEF", "DEF%", "HP", "HP%"],
    "Earring": ["MP MAX"]
}

SECONDARY_STATS_OPTIONS = [
    "ATK", "ATK%", "ATK% +3/4",
    "DEF", "DEF%", "DEF% +3/4",
    "HP", "HP%", "HP% +3/4",
    "CRIT HIT",
    "CRIT DMG",
    "DMG INC",
    "DEF PEN",
    "MP CONS",
    "MP MAX",
    "MP Regen %",
    "DMG RES"
]

FOCUS_STATS_OPTIONS = [
    "ATK",
    "DEF",
    "HP",
    "CRIT HIT",
    "CRIT DMG",
    "DMG INC",
    "DEF PEN",
    "MP CONS",
    "MP MAX",
    "MP Regen%",
    "DMG RES"
]

CORE_MAIN_STATS = {
    "01": ["ATK", "ATK%"],
    "02": ["DEF", "DEF%"],
    "03": ["HP", "HP%"]
}

CORE_SECONDARY_STATS = {
    "01": ["CRIT HIT", "CRIT DMG", "DMG INC", "DEF PEN", "MP CONS", "MP MAX"],
    "02": ["CRIT HIT", "CRIT DMG", "DMG INC", "DEF PEN", "MP CONS", "MP MAX"],
    "03": ["CRIT HIT", "CRIT DMG", "DMG INC", "DEF PEN", "MP CONS", "MP MAX"]
}
