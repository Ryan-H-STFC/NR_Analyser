from os import listdir, fsdecode

from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
)
from project.myPyQt.PeriodicCell import ElementCell
from project.helpers.resourcePath import resource_path
from project.helpers.interpName import interpName
from project.settings import params

isotopes = []
elements = []
for file in listdir(resource_path(f"{params['dir_graphData']}")):
    filename = fsdecode(file)
    if ".csv" not in filename[-4:]:
        continue
    filename = filename[:-4]
    info = interpName(filename)
    if info['nNum'] is None:
        elements.append(filename.removeprefix('element_'))
    else:
        isotopes.append(filename)

pass

periodic_table = {
    "H": {
        "nNum": 1,
        "name": "Hydrogen",
        "weight": 1.00784,
        "type": "Reactive Non-Metal"
    },
    "He": {
        "nNum": 2,
        "name": "Helium",
        "weight": 4.002602,
        "type": "Noble Gases"
    },
    "Li": {
        "nNum": 3,
        "name": "Lithium",
        "weight": 6.94,
        "type": "Alkali Metal"
    },
    "Be": {
        "nNum": 4,
        "name": "Beryllium",
        "weight": 9.012182,
        "type": "Alkaline Earth Metal"
    },
    "B": {
        "nNum": 5,
        "name": "Boron",
        "weight": 10.81,
        "type": "Metalloid"
    },
    "C": {
        "nNum": 6,
        "name": "Carbon",
        "weight": 12.011,
        "type": "Reactive Non-Metal"
    },
    "N": {
        "nNum": 7,
        "name": "Nitrogen",
        "weight": 14.00674,
        "type": "Reactive Non-Metal"
    },
    "O": {
        "nNum": 8,
        "name": "Oxygen",
        "weight": 15.9994,
        "type": "Reactive Non-Metal"
    },
    "F": {
        "nNum": 9,
        "name": "Fluorine",
        "weight": 18.9984032,
        "type": "Reactive Non-Metal"
    },
    "Ne": {
        "nNum": 10,
        "name": "Neon",
        "weight": 20.1797,
        "type": "Noble Gases"
    },
    "Na": {
        "nNum": 11,
        "name": "Sodium",
        "weight": 22.98976928,
        "type": "Alkali Metal"
    },
    "Mg": {
        "nNum": 12,
        "name": "Magnesium",
        "weight": 24.305,
        "type": "Alkaline Earth Metal"
    },
    "Al": {
        "nNum": 13,
        "name": "Aluminium",
        "weight": 26.9815386,
        "type": "Post-Transition Metal"
    },
    "Si": {
        "nNum": 14,
        "name": "Silicon",
        "weight": 28.0855,
        "type": "Metalloid"
    },
    "P": {
        "nNum": 15,
        "name": "Phosphorus",
        "weight": 30.973762,
        "type": "Reactive Non-Metal"
    },
    "S": {
        "nNum": 16,
        "name": "Sulfur",
        "weight": 32.06,
        "type": "Reactive Non-Metal"
    },
    "Cl": {
        "nNum": 17,
        "name": "Chlorine",
        "weight": 35.45,
        "type": "Reactive Non-Metal"
    },
    "Ar": {
        "nNum": 18,
        "name": "Argon",
        "weight": 39.948,
        "type": "Noble Gases"
    },
    "K": {
        "nNum": 19,
        "name": "Potassium",
        "weight": 39.0983,
        "type": "Alkali Metal"
    },
    "Ca": {
        "nNum": 20,
        "name": "Calcium",
        "weight": 40.078,
        "type": "Alkaline Earth Metal"
    },
    "Sc": {
        "nNum": 21,
        "name": "Scandium",
        "weight": 44.955912,
        "type": "Transtion Metal"
    },
    "Ti": {
        "nNum": 22,
        "name": "Titanium",
        "weight": 47.867,
        "type": "Transtion Metal"
    },
    "V": {
        "nNum": 23,
        "name": "Vanadium",
        "weight": 50.9415,
        "type": "Transtion Metal"
    },
    "Cr": {
        "nNum": 24,
        "name": "Chromium",
        "weight": 51.9961,
        "type": "Transtion Metal"
    },
    "Mn": {
        "nNum": 25,
        "name": "Manganese",
        "weight": 54.938045,
        "type": "Transtion Metal"
    },
    "Fe": {
        "nNum": 26,
        "name": "Iron",
        "weight": 55.847,
        "type": "Transtion Metal"
    },
    "Co": {
        "nNum": 27,
        "name": "Cobalt",
        "weight": 58.933195,
        "type": "Transtion Metal"
    },
    "Ni": {
        "nNum": 28,
        "name": "Nickel",
        "weight": 58.6934,
        "type": "Transtion Metal"
    },
    "Cu": {
        "nNum": 29,
        "name": "Copper",
        "weight": 63.546,
        "type": "Transtion Metal"
    },
    "Zn": {
        "nNum": 30,
        "name": "Zinc",
        "weight": 65.38,
        "type": "Transtion Metal"
    },
    "Ga": {
        "nNum": 31,
        "name": "Gallium",
        "weight": 69.723,
        "type": "Post-Transition Metal"
    },
    "Ge": {
        "nNum": 32,
        "name": "Germanium",
        "weight": 72.64,
        "type": "Metalloid"
    },
    "As": {
        "nNum": 33,
        "name": "Arsenic",
        "weight": 74.9216,
        "type": "Metalloid"
    },
    "Se": {
        "nNum": 34,
        "name": "Selenium",
        "weight": 78.971,
        "type": "Reactive Non-Metal"
    },
    "Br": {
        "nNum": 35,
        "name": "Bromine",
        "weight": 79.904,
        "type": "Reactive Non-Metal"
    },
    "Kr": {
        "nNum": 36,
        "name": "Krypton",
        "weight": 83.798,
        "type": "Noble Gases"
    },
    "Rb": {
        "nNum": 37,
        "name": "Rubidium",
        "weight": 85.4678,
        "type": "Alkali Metal"
    },
    "Sr": {
        "nNum": 38,
        "name": "Strontium",
        "weight": 87.62,
        "type": "Alkaline Earth Metal"
    },
    "Y": {
        "nNum": 39,
        "name": "Yttrium",
        "weight": 88.90585,
        "type": "Transtion Metal"
    },
    "Zr": {
        "nNum": 40,
        "name": "Zirconium",
        "weight": 91.224,
        "type": "Transtion Metal"
    },
    "Nb": {
        "nNum": 41,
        "name": "Niobium",
        "weight": 92.90638,
        "type": "Transtion Metal"
    },
    "Mo": {
        "nNum": 42,
        "name": "Molybdenum",
        "weight": 95.95,
        "type": "Transtion Metal"
    },
    "Tc": {
        "nNum": 43,
        "name": "Technetium",
        "weight": "(98)",
        "type": "Transtion Metal"
    },
    "Ru": {
        "nNum": 44,
        "name": "Ruthenium",
        "weight": 101.07,
        "type": "Transtion Metal"
    },
    "Rh": {
        "nNum": 45,
        "name": "Rhodium",
        "weight": 102.9055,
        "type": "Transtion Metal"
    },
    "Pd": {
        "nNum": 46,
        "name": "Palladium",
        "weight": 106.42,
        "type": "Transtion Metal"
    },
    "Ag": {
        "nNum": 47,
        "name": "Silver",
        "weight": 107.8682,
        "type": "Transtion Metal"
    },
    "Cd": {
        "nNum": 48,
        "name": "Cadmium",
        "weight": 112.411,
        "type": "Transtion Metal"
    },
    "In": {
        "nNum": 49,
        "name": "Indium",
        "weight": 114.818,
        "type": "Post-Transition Metal"
    },
    "Sn": {
        "nNum": 50,
        "name": "Tin",
        "weight": 118.71,
        "type": "Post-Transition Metal"
    },
    "Sb": {
        "nNum": 51,
        "name": "Antimony",
        "weight": 121.76,
        "type": "Metalloid"
    },
    "Te": {
        "nNum": 52,
        "name": "Tellurium",
        "weight": 127.6,
        "type": "Metalloid"
    },
    "I": {
        "nNum": 53,
        "name": "Iodine",
        "weight": 126.90447,
        "type": "Reactive Non-Metal"
    },
    "Xe": {
        "nNum": 54,
        "name": "Xenon",
        "weight": 131.293,
        "type": "Noble Gases"
    },
    "Cs": {
        "nNum": 55,
        "name": "Caesium",
        "weight": 132.9054519,
        "type": "Alkali Metal"
    },
    "Ba": {
        "nNum": 56,
        "name": "Barium",
        "weight": 137.327,
        "type": "Alkaline Earth Metal"
    },
    "La": {
        "nNum": 57,
        "name": "Lanthanum",
        "weight": 138.90547,
        "type": "Lanthanoid"
    },
    "Ce": {
        "nNum": 58,
        "name": "Cerium",
        "weight": 140.116,
        "type": "Lanthanoid"
    },
    "Pr": {
        "nNum": 59,
        "name": "Praseodymium",
        "weight": 140.90765,
        "type": "Lanthanoid"
    },
    "Nd": {
        "nNum": 60,
        "name": "Neodymium",
        "weight": 144.242,
        "type": "Lanthanoid"
    },
    "Pm": {
        "nNum": 61,
        "name": "Promethium",
        "weight": "(145)",
        "type": "Lanthanoid"
    },
    "Sm": {
        "nNum": 62,
        "name": "Samarium",
        "weight": 150.36,
        "type": "Lanthanoid"
    },
    "Eu": {
        "nNum": 63,
        "name": "Europium",
        "weight": 151.964,
        "type": "Lanthanoid"
    },
    "Gd": {
        "nNum": 64,
        "name": "Gadolinium",
        "weight": 157.25,
        "type": "Lanthanoid"
    },
    "Tb": {
        "nNum": 65,
        "name": "Terbium",
        "weight": 158.92535,
        "type": "Lanthanoid"
    },
    "Dy": {
        "nNum": 66,
        "name": "Dysprosium",
        "weight": 162.5,
        "type": "Lanthanoid"
    },
    "Ho": {
        "nNum": 67,
        "name": "Holmium",
        "weight": 164.93032,
        "type": "Lanthanoid"
    },
    "Er": {
        "nNum": 68,
        "name": "Erbium",
        "weight": 167.259,
        "type": "Lanthanoid"
    },
    "Tm": {
        "nNum": 69,
        "name": "Thulium",
        "weight": 168.93422,
        "type": "Lanthanoid"
    },
    "Yb": {
        "nNum": 70,
        "name": "Ytterbium",
        "weight": 173.054,
        "type": "Lanthanoid"
    },
    "Lu": {
        "nNum": 71,
        "name": "Lutetium",
        "weight": 174.9668,
        "type": "Lanthanoid"
    },
    "Hf": {
        "nNum": 72,
        "name": "Hafnium",
        "weight": 178.49,
        "type": "Transtion Metal"
    },
    "Ta": {
        "nNum": 73,
        "name": "Tantalum",
        "weight": 180.94788,
        "type": "Transtion Metal"
    },
    "W": {
        "nNum": 74,
        "name": "Tungsten",
        "weight": 183.84,
        "type": "Transtion Metal"
    },
    "Re": {
        "nNum": 75,
        "name": "Rhenium",
        "weight": 186.207,
        "type": "Transtion Metal"
    },
    "Os": {
        "nNum": 76,
        "name": "Osmium",
        "weight": 190.23,
        "type": "Transtion Metal"
    },
    "Ir": {
        "nNum": 77,
        "name": "Iridium",
        "weight": 192.217,
        "type": "Transtion Metal"
    },
    "Pt": {
        "nNum": 78,
        "name": "Platinum",
        "weight": 195.084,
        "type": "Transtion Metal"
    },
    "Au": {
        "nNum": 79,
        "name": "Gold",
        "weight": 196.966569,
        "type": "Transtion Metal"
    },
    "Hg": {
        "nNum": 80,
        "name": "Mercury",
        "weight": 200.592,
        "type": "Transtion Metal"
    },
    "Tl": {
        "nNum": 81,
        "name": "Thallium",
        "weight": 204.3833,
        "type": "Post-Transition Metal"
    },
    "Pb": {
        "nNum": 82,
        "name": "Lead",
        "weight": 207.2,
        "type": "Post-Transition Metal"
    },
    "Bi": {
        "nNum": 83,
        "name": "Bismuth",
        "weight": 208.9804,
        "type": "Post-Transition Metal"
    },
    "Po": {
        "nNum": 84,
        "name": "Polonium",
        "weight": "(209)",
        "type": "Post-Transition Metal"
    },
    "At": {
        "nNum": 85,
        "name": "Astatine",
        "weight": "(210)",
        "type": "Metalloid"
    },
    "Rn": {
        "nNum": 86,
        "name": "Radon",
        "weight": "(222.0176)",
        "type": "Noble Gases"
    },
    "Fr": {
        "nNum": 87,
        "name": "Francium",
        "weight": "(223)",
        "type": "Alkali Metal"
    },
    "Ra": {
        "nNum": 88,
        "name": "Radium",
        "weight": "(226)",
        "type": "Alkaline Earth Metal"
    },
    "Ac": {
        "nNum": 89,
        "name": "Actinium",
        "weight": "(227)",
        "type": "Actinoid"
    },
    "Th": {
        "nNum": 90,
        "name": "Thorium",
        "weight": 232.03806,
        "type": "Actinoid"
    },
    "Pa": {
        "nNum": 91,
        "name": "Protactinium",
        "weight": 231.03588,
        "type": "Actinoid"
    },
    "U": {
        "nNum": 92,
        "name": "Uranium",
        "weight": 238.02891,
        "type": "Actinoid"
    },
    "Np": {
        "nNum": 93,
        "name": "Neptunium",
        "weight": "(237.0482)",
        "type": "Actinoid"
    },
    "Pu": {
        "nNum": 94,
        "name": "Plutonium",
        "weight": "(244.0642)",
        "type": "Actinoid"
    },
    "Am": {
        "nNum": 95,
        "name": "Americium",
        "weight": "(243.0614)",
        "type": "Actinoid"
    },
    "Cm": {
        "nNum": 96,
        "name": "Curium",
        "weight": "(247.0703)",
        "type": "Actinoid"
    },
    "Bk": {
        "nNum": 97,
        "name": "Berkelium",
        "weight": "(247.0703)",
        "type": "Actinoid"
    },
    "Cf": {
        "nNum": 98,
        "name": "Californium",
        "weight": "(251.0796)",
        "type": "Actinoid"
    },
    "Es": {
        "nNum": 99,
        "name": "Einsteinium",
        "weight": "(252.083)",
        "type": "Actinoid"
    },
    "Fm": {
        "nNum": 100,
        "name": "Fermium",
        "weight": "(257.0951)",
        "type": "Actinoid"
    },
    "Md": {
        "nNum": 101,
        "name": "Mendelevium",
        "weight": "(258.100)",
        "type": "Actinoid"
    },
    "No": {
        "nNum": 102,
        "name": "Nobelium",
        "weight": "(259.101)",
        "type": "Actinoid"
    },
    "Lr": {
        "nNum": 103,
        "name": "Lawrencium",
        "weight": "(262.110)",
        "type": "Actinoid"
    },
    "Rf": {
        "nNum": 104,
        "name": "Rutherfordium",
        "weight": "(267.122)",
        "type": "Transactinide"
    },
    "Db": {
        "nNum": 105,
        "name": "Dubnium",
        "weight": "(268.127)",
        "type": "Transactinide"
    },
    "Sg": {
        "nNum": 106,
        "name": "Seaborgium",
        "weight": "(271.133)",
        "type": "Transactinide"
    },
    "Bh": {
        "nNum": 107,
        "name": "Bohrium",
        "weight": 272.138,
        "type": "Transactinide"},
    "Hs": {
        "nNum": 108,
        "name": "Hassium",
        "weight": "(270.150)",
        "type": "Transactinide"
    },
    "Mt": {
        "nNum": 109,
        "name": "Meitnerium",
        "weight": "(278.170)",
        "type": "Transactinide"
    },
    "Ds": {
        "nNum": 110,
        "name": "Darmstadtium",
        "weight": "(281.175)",
        "type": "Transactinide"
    },
    "Rg": {
        "nNum": 111,
        "name": "Roentgenium",
        "weight": "(282.178)",
        "type": "Transactinide"
    },
    "Cn": {
        "nNum": 112,
        "name": "Copernicium",
        "weight": "(285.185)",
        "type": "Transactinide"
    },
    "Nh": {
        "nNum": 113,
        "name": "Nihonium",
        "weight": "(286.190)",
        "type": "Superactinide"
    },
    "Fl": {
        "nNum": 114,
        "name": "Flerovium",
        "weight": "(289.198)",
        "type": "Superactinide"
    },
    "Mc": {
        "nNum": 115,
        "name": "Moscovium",
        "weight": "(290.200)",
        "type": "Superactinide"
    },
    "Lv": {
        "nNum": 116,
        "name": "Livermorium",
        "weight": "(293.210)",
        "type": "Superactinide"
    },
    "Ts": {
        "nNum": 117,
        "name": "Tennessine",
        "weight": "(294.216)",
        "type": "Superactinide"
    },
    "Og": {
        "nNum": 118,
        "name": "Oganesson",
        "weight": "(294.220)",
        "type": "Noble Gas"
    }
}


class QtPeriodicTable(QDialog):

    def __init__(self) -> None:
        self.grid = QGridLayout(self)
