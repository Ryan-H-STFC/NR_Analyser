from os import listdir, fsdecode
from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,

)
from qtwidgets import AnimatedToggle
from PyQt6.QtCore import Qt, QModelIndex

from project.myPyQt.PeriodicCell import ElementCell
from project.myPyQt.SquareGrid import SquareGrid
from project.helpers.resourcePath import resource_path
from project.helpers.interpName import interpName, constructName
from project.helpers.getWidgets import getLayoutWidgets
from project.settings import params

from math import floor

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
        "symbol": "H",
        "nNum": 1,
        "name": "Hydrogen",
        "weight": 1.00784,
        "type": "Reactive Non-Metal",
        "pos": (1, 1)
    },
    "He": {
        "symbol": "He",
        "nNum": 2,
        "name": "Helium",
        "weight": 4.002602,
        "type": "Noble Gas",
        "pos": (1, 18)
    },
    "Li": {
        "symbol": "Li",
        "nNum": 3,
        "name": "Lithium",
        "weight": 6.94,
        "type": "Alkali Metal",
        "pos": (2, 1)
    },
    "Be": {
        "symbol": "Be",
        "nNum": 4,
        "name": "Beryllium",
        "weight": 9.012182,
        "type": "Alkaline Earth Metal",
        "pos": (2, 2)
    },
    "B": {
        "symbol": "B",
        "nNum": 5,
        "name": "Boron",
        "weight": 10.81,
        "type": "Metalloid",
        "pos": (2, 13)
    },
    "C": {
        "symbol": "C",
        "nNum": 6,
        "name": "Carbon",
        "weight": 12.011,
        "type": "Reactive Non-Metal",
        "pos": (2, 14)
    },
    "N": {
        "symbol": "N",
        "nNum": 7,
        "name": "Nitrogen",
        "weight": 14.00674,
        "type": "Reactive Non-Metal",
        "pos": (2, 15)
    },
    "O": {
        "symbol": "O",
        "nNum": 8,
        "name": "Oxygen",
        "weight": 15.9994,
        "type": "Reactive Non-Metal",
        "pos": (2, 16)
    },
    "F": {
        "symbol": "F",
        "nNum": 9,
        "name": "Fluorine",
        "weight": 18.9984032,
        "type": "Reactive Non-Metal",
        "pos": (2, 17)
    },
    "Ne": {
        "symbol": "Ne",
        "nNum": 10,
        "name": "Neon",
        "weight": 20.1797,
        "type": "Noble Gas",
        "pos": (2, 18)
    },
    "Na": {
        "symbol": "Na",
        "nNum": 11,
        "name": "Sodium",
        "weight": 22.98976928,
        "type": "Alkali Metal",
        "pos": (3, 1)
    },
    "Mg": {
        "symbol": "Mg",
        "nNum": 12,
        "name": "Magnesium",
        "weight": 24.305,
        "type": "Alkaline Earth Metal",
        "pos": (3, 2)
    },
    "Al": {
        "symbol": "Al",
        "nNum": 13,
        "name": "Aluminium",
        "weight": 26.9815386,
        "type": "Post-Transition Metal",
        "pos": (3, 13)
    },
    "Si": {
        "symbol": "Si",
        "nNum": 14,
        "name": "Silicon",
        "weight": 28.0855,
        "type": "Metalloid",
        "pos": (3, 14)
    },
    "P": {
        "symbol": "P",
        "nNum": 15,
        "name": "Phosphorus",
        "weight": 30.973762,
        "type": "Reactive Non-Metal",
        "pos": (3, 15)
    },
    "S": {
        "symbol": "S",
        "nNum": 16,
        "name": "Sulfur",
        "weight": 32.06,
        "type": "Reactive Non-Metal",
        "pos": (3, 16)
    },
    "Cl": {
        "symbol": "Cl",
        "nNum": 17,
        "name": "Chlorine",
        "weight": 35.45,
        "type": "Reactive Non-Metal",
        "pos": (3, 17)
    },
    "Ar": {
        "symbol": "Ar",
        "nNum": 18,
        "name": "Argon",
        "weight": 39.948,
        "type": "Noble Gas",
        "pos": (3, 18)
    },
    "K": {
        "symbol": "K",
        "nNum": 19,
        "name": "Potassium",
        "weight": 39.0983,
        "type": "Alkali Metal",
        "pos": (4, 1)
    },
    "Ca": {
        "symbol": "Ca",
        "nNum": 20,
        "name": "Calcium",
        "weight": 40.078,
        "type": "Alkaline Earth Metal",
        "pos": (4, 2)
    },
    "Sc": {
        "symbol": "Sc",
        "nNum": 21,
        "name": "Scandium",
        "weight": 44.955912,
        "type": "Transition Metal",
        "pos": (4, 3)
    },
    "Ti": {
        "symbol": "Ti",
        "nNum": 22,
        "name": "Titanium",
        "weight": 47.867,
        "type": "Transition Metal",
        "pos": (4, 4)
    },
    "V": {
        "symbol": "V",
        "nNum": 23,
        "name": "Vanadium",
        "weight": 50.9415,
        "type": "Transition Metal",
        "pos": (4, 5)
    },
    "Cr": {
        "symbol": "Cr",
        "nNum": 24,
        "name": "Chromium",
        "weight": 51.9961,
        "type": "Transition Metal",
        "pos": (4, 6)
    },
    "Mn": {
        "symbol": "Mn",
        "nNum": 25,
        "name": "Manganese",
        "weight": 54.938045,
        "type": "Transition Metal",
        "pos": (4, 7)
    },
    "Fe": {
        "symbol": "Fe",
        "nNum": 26,
        "name": "Iron",
        "weight": 55.847,
        "type": "Transition Metal",
        "pos": (4, 8)
    },
    "Co": {
        "symbol": "Co",
        "nNum": 27,
        "name": "Cobalt",
        "weight": 58.933195,
        "type": "Transition Metal",
        "pos": (4, 9)
    },
    "Ni": {
        "symbol": "Ni",
        "nNum": 28,
        "name": "Nickel",
        "weight": 58.6934,
        "type": "Transition Metal",
        "pos": (4, 10)
    },
    "Cu": {
        "symbol": "Cu",
        "nNum": 29,
        "name": "Copper",
        "weight": 63.546,
        "type": "Transition Metal",
        "pos": (4, 11)
    },
    "Zn": {
        "symbol": "Zn",
        "nNum": 30,
        "name": "Zinc",
        "weight": 65.38,
        "type": "Transition Metal",
        "pos": (4, 12)
    },
    "Ga": {
        "symbol": "Ga",
        "nNum": 31,
        "name": "Gallium",
        "weight": 69.723,
        "type": "Post-Transition Metal",
        "pos": (4, 13)
    },
    "Ge": {
        "symbol": "Ge",
        "nNum": 32,
        "name": "Germanium",
        "weight": 72.64,
        "type": "Metalloid",
        "pos": (4, 14)
    },
    "As": {
        "symbol": "As",
        "nNum": 33,
        "name": "Arsenic",
        "weight": 74.9216,
        "type": "Metalloid",
        "pos": (4, 15)
    },
    "Se": {
        "symbol": "Se",
        "nNum": 34,
        "name": "Selenium",
        "weight": 78.971,
        "type": "Reactive Non-Metal",
        "pos": (4, 16)
    },
    "Br": {
        "symbol": "Br",
        "nNum": 35,
        "name": "Bromine",
        "weight": 79.904,
        "type": "Reactive Non-Metal",
        "pos": (4, 17)
    },
    "Kr": {
        "symbol": "Kr",
        "nNum": 36,
        "name": "Krypton",
        "weight": 83.798,
        "type": "Noble Gas",
        "pos": (4, 18)
    },
    "Rb": {
        "symbol": "Rb",
        "nNum": 37,
        "name": "Rubidium",
        "weight": 85.4678,
        "type": "Alkali Metal",
        "pos": (5, 1)
    },
    "Sr": {
        "symbol": "Sr",
        "nNum": 38,
        "name": "Strontium",
        "weight": 87.62,
        "type": "Alkaline Earth Metal",
        "pos": (5, 2)
    },
    "Y": {
        "symbol": "Y",
        "nNum": 39,
        "name": "Yttrium",
        "weight": 88.90585,
        "type": "Transition Metal",
        "pos": (5, 3)
    },
    "Zr": {
        "symbol": "Zr",
        "nNum": 40,
        "name": "Zirconium",
        "weight": 91.224,
        "type": "Transition Metal",
        "pos": (5, 4)
    },
    "Nb": {
        "symbol": "Nb",
        "nNum": 41,
        "name": "Niobium",
        "weight": 92.90638,
        "type": "Transition Metal",
        "pos": (5, 5)
    },
    "Mo": {
        "symbol": "Mo",
        "nNum": 42,
        "name": "Molybdenum",
        "weight": 95.95,
        "type": "Transition Metal",
        "pos": (5, 6)
    },
    "Tc": {
        "symbol": "Tc",
        "nNum": 43,
        "name": "Technetium",
        "weight": "(98)",
        "type": "Transition Metal",
        "pos": (5, 7)
    },
    "Ru": {
        "symbol": "Ru",
        "nNum": 44,
        "name": "Ruthenium",
        "weight": 101.07,
        "type": "Transition Metal",
        "pos": (5, 8)
    },
    "Rh": {
        "symbol": "Rh",
        "nNum": 45,
        "name": "Rhodium",
        "weight": 102.9055,
        "type": "Transition Metal",
        "pos": (5, 9)
    },
    "Pd": {
        "symbol": "Pd",
        "nNum": 46,
        "name": "Palladium",
        "weight": 106.42,
        "type": "Transition Metal",
        "pos": (5, 10)
    },
    "Ag": {
        "symbol": "Ag",
        "nNum": 47,
        "name": "Silver",
        "weight": 107.8682,
        "type": "Transition Metal",
        "pos": (5, 11)
    },
    "Cd": {
        "symbol": "Cd",
        "nNum": 48,
        "name": "Cadmium",
        "weight": 112.411,
        "type": "Transition Metal",
        "pos": (5, 12)
    },
    "In": {
        "symbol": "In",
        "nNum": 49,
        "name": "Indium",
        "weight": 114.818,
        "type": "Post-Transition Metal",
        "pos": (5, 13)
    },
    "Sn": {
        "symbol": "Sn",
        "nNum": 50,
        "name": "Tin",
        "weight": 118.71,
        "type": "Post-Transition Metal",
        "pos": (5, 14)
    },
    "Sb": {
        "symbol": "Sb",
        "nNum": 51,
        "name": "Antimony",
        "weight": 121.76,
        "type": "Metalloid",
        "pos": (5, 15)
    },
    "Te": {
        "symbol": "Te",
        "nNum": 52,
        "name": "Tellurium",
        "weight": 127.6,
        "type": "Metalloid",
        "pos": (5, 16)
    },
    "I": {
        "symbol": "I",
        "nNum": 53,
        "name": "Iodine",
        "weight": 126.90447,
        "type": "Reactive Non-Metal",
        "pos": (5, 17)
    },
    "Xe": {
        "symbol": "Xe",
        "nNum": 54,
        "name": "Xenon",
        "weight": 131.293,
        "type": "Noble Gas",
        "pos": (5, 18)
    },
    "Cs": {
        "symbol": "Cs",
        "nNum": 55,
        "name": "Caesium",
        "weight": 132.9054519,
        "type": "Alkali Metal",
        "pos": (6, 1)
    },
    "Ba": {
        "symbol": "Ba",
        "nNum": 56,
        "name": "Barium",
        "weight": 137.327,
        "type": "Alkaline Earth Metal",
        "pos": (6, 2)
    },
    "57-71": {
        "symbol": "57-71",
        "nNum": None,
        "name": None,
        "weight": None,
        "type": "Lanthanoid",
        "pos": (6, 3)
    },
    "La": {
        "symbol": "La",
        "nNum": 57,
        "name": "Lanthanum",
        "weight": 138.90547,
        "type": "Lanthanoid",
        "pos": (6, 4.1)
    },
    "Ce": {
        "symbol": "Ce",
        "nNum": 58,
        "name": "Cerium",
        "weight": 140.116,
        "type": "Lanthanoid",
        "pos": (6, 5.1)
    },
    "Pr": {
        "symbol": "Pr",
        "nNum": 59,
        "name": "Praseodymium",
        "weight": 140.90765,
        "type": "Lanthanoid",
        "pos": (6, 6.1)
    },
    "Nd": {
        "symbol": "Nd",
        "nNum": 60,
        "name": "Neodymium",
        "weight": 144.242,
        "type": "Lanthanoid",
        "pos": (6, 7.1)
    },
    "Pm": {
        "symbol": "Pm",
        "nNum": 61,
        "name": "Promethium",
        "weight": "(145)",
        "type": "Lanthanoid",
        "pos": (6, 8.1)
    },
    "Sm": {
        "symbol": "Sm",
        "nNum": 62,
        "name": "Samarium",
        "weight": 150.36,
        "type": "Lanthanoid",
        "pos": (6, 9.1)
    },
    "Eu": {
        "symbol": "Eu",
        "nNum": 63,
        "name": "Europium",
        "weight": 151.964,
        "type": "Lanthanoid",
        "pos": (6, 10.1)
    },
    "Gd": {
        "symbol": "Gd",
        "nNum": 64,
        "name": "Gadolinium",
        "weight": 157.25,
        "type": "Lanthanoid",
        "pos": (6, 11.1)
    },
    "Tb": {
        "symbol": "Tb",
        "nNum": 65,
        "name": "Terbium",
        "weight": 158.92535,
        "type": "Lanthanoid",
        "pos": (6, 12.1)
    },
    "Dy": {
        "symbol": "Dy",
        "nNum": 66,
        "name": "Dysprosium",
        "weight": 162.1,
        "type": "Lanthanoid",
        "pos": (6, 13.1)
    },
    "Ho": {
        "symbol": "Ho",
        "nNum": 67,
        "name": "Holmium",
        "weight": 164.93032,
        "type": "Lanthanoid",
        "pos": (6, 14.1)
    },
    "Er": {
        "symbol": "Er",
        "nNum": 68,
        "name": "Erbium",
        "weight": 167.259,
        "type": "Lanthanoid",
        "pos": (6, 15.1)
    },
    "Tm": {
        "symbol": "Tm",
        "nNum": 69,
        "name": "Thulium",
        "weight": 168.93422,
        "type": "Lanthanoid",
        "pos": (6, 16.1)
    },
    "Yb": {
        "symbol": "Yb",
        "nNum": 70,
        "name": "Ytterbium",
        "weight": 173.054,
        "type": "Lanthanoid",
        "pos": (6, 17.1)
    },
    "Lu": {
        "symbol": "Lu",
        "nNum": 71,
        "name": "Lutetium",
        "weight": 174.9668,
        "type": "Lanthanoid",
        "pos": (6, 18.1)
    },
    "Hf": {
        "symbol": "Hf",
        "nNum": 72,
        "name": "Hafnium",
        "weight": 178.49,
        "type": "Transition Metal",
        "pos": (6, 4)
    },
    "Ta": {
        "symbol": "Ta",
        "nNum": 73,
        "name": "Tantalum",
        "weight": 180.94788,
        "type": "Transition Metal",
        "pos": (6, 5)
    },
    "W": {
        "symbol": "W",
        "nNum": 74,
        "name": "Tungsten",
        "weight": 183.84,
        "type": "Transition Metal",
        "pos": (6, 6)
    },
    "Re": {
        "symbol": "Re",
        "nNum": 75,
        "name": "Rhenium",
        "weight": 186.207,
        "type": "Transition Metal",
        "pos": (6, 7)
    },
    "Os": {
        "symbol": "Os",
        "nNum": 76,
        "name": "Osmium",
        "weight": 190.23,
        "type": "Transition Metal",
        "pos": (6, 8)
    },
    "Ir": {
        "symbol": "Ir",
        "nNum": 77,
        "name": "Iridium",
        "weight": 192.217,
        "type": "Transition Metal",
        "pos": (6, 9)
    },
    "Pt": {
        "symbol": "Pt",
        "nNum": 78,
        "name": "Platinum",
        "weight": 195.084,
        "type": "Transition Metal",
        "pos": (6, 10)
    },
    "Au": {
        "symbol": "Au",
        "nNum": 79,
        "name": "Gold",
        "weight": 196.966569,
        "type": "Transition Metal",
        "pos": (6, 11)
    },
    "Hg": {
        "symbol": "Hg",
        "nNum": 80,
        "name": "Mercury",
        "weight": 200.592,
        "type": "Transition Metal",
        "pos": (6, 12)
    },
    "Tl": {
        "symbol": "Tl",
        "nNum": 81,
        "name": "Thallium",
        "weight": 204.3833,
        "type": "Post-Transition Metal",
        "pos": (6, 13)
    },
    "Pb": {
        "symbol": "Pb",
        "nNum": 82,
        "name": "Lead",
        "weight": 207.2,
        "type": "Post-Transition Metal",
        "pos": (6, 14)
    },
    "Bi": {
        "symbol": "Bi",
        "nNum": 83,
        "name": "Bismuth",
        "weight": 208.9804,
        "type": "Post-Transition Metal",
        "pos": (6, 15)
    },
    "Po": {
        "symbol": "Po",
        "nNum": 84,
        "name": "Polonium",
        "weight": "(209)",
        "type": "Post-Transition Metal",
        "pos": (6, 16)
    },
    "At": {
        "symbol": "At",
        "nNum": 85,
        "name": "Astatine",
        "weight": "(210)",
        "type": "Metalloid",
        "pos": (6, 17)
    },
    "Rn": {
        "symbol": "Rn",
        "nNum": 86,
        "name": "Radon",
        "weight": "(222.0176)",
        "type": "Noble Gas",
        "pos": (6, 18)
    },
    "Fr": {
        "symbol": "Fr",
        "nNum": 87,
        "name": "Francium",
        "weight": "(223)",
        "type": "Alkali Metal",
        "pos": (7, 1)
    },
    "Ra": {
        "symbol": "Ra",
        "nNum": 88,
        "name": "Radium",
        "weight": "(226)",
        "type": "Alkaline Earth Metal",
        "pos": (7, 2)
    },
    "79-103": {
        "symbol": "79-103",
        "nNum": None,
        "name": None,
        "weight": None,
        "type": "Actinoid",
        "pos": (7, 3)
    },
    "Ac": {
        "symbol": "Ac",
        "nNum": 89,
        "name": "Actinium",
        "weight": "(227)",
        "type": "Actinoid",
        "pos": (7, 4.2)
    },
    "Th": {
        "symbol": "Th",
        "nNum": 90,
        "name": "Thorium",
        "weight": 232.03806,
        "type": "Actinoid",
        "pos": (7, 5.2)
    },
    "Pa": {
        "symbol": "Pa",
        "nNum": 91,
        "name": "Protactinium",
        "weight": 231.03588,
        "type": "Actinoid",
        "pos": (7, 6.2)
    },
    "U": {
        "symbol": "U",
        "nNum": 92,
        "name": "Uranium",
        "weight": 238.02891,
        "type": "Actinoid",
        "pos": (7, 7.2)
    },
    "Np": {
        "symbol": "Np",
        "nNum": 93,
        "name": "Neptunium",
        "weight": "(237.0482)",
        "type": "Actinoid",
        "pos": (7, 8.2)
    },
    "Pu": {
        "symbol": "Pu",
        "nNum": 94,
        "name": "Plutonium",
        "weight": "(244.0642)",
        "type": "Actinoid",
        "pos": (7, 9.2)
    },
    "Am": {
        "symbol": "Am",
        "nNum": 95,
        "name": "Americium",
        "weight": "(243.0614)",
        "type": "Actinoid",
        "pos": (7, 10.2)
    },
    "Cm": {
        "symbol": "Cm",
        "nNum": 96,
        "name": "Curium",
        "weight": "(247.0703)",
        "type": "Actinoid",
        "pos": (7, 11.2)
    },
    "Bk": {
        "symbol": "Bk",
        "nNum": 97,
        "name": "Berkelium",
        "weight": "(247.0703)",
        "type": "Actinoid",
        "pos": (7, 12.2)
    },
    "Cf": {
        "symbol": "Cf",
        "nNum": 98,
        "name": "Californium",
        "weight": "(251.0796)",
        "type": "Actinoid",
        "pos": (7, 13.2)
    },
    "Es": {
        "symbol": "Es",
        "nNum": 99,
        "name": "Einsteinium",
        "weight": "(252.083)",
        "type": "Actinoid",
        "pos": (7, 14.2)
    },
    "Fm": {
        "symbol": "Fm",
        "nNum": 100,
        "name": "Fermium",
        "weight": "(257.0951)",
        "type": "Actinoid",
        "pos": (7, 15.2)
    },
    "Md": {
        "symbol": "Md",
        "nNum": 101,
        "name": "Mendelevium",
        "weight": "(258.100)",
        "type": "Actinoid",
        "pos": (7, 16.2)
    },
    "No": {
        "symbol": "No",
        "nNum": 102,
        "name": "Nobelium",
        "weight": "(259.101)",
        "type": "Actinoid",
        "pos": (7, 17.2)
    },
    "Lr": {
        "symbol": "Lr",
        "nNum": 103,
        "name": "Lawrencium",
        "weight": "(262.110)",
        "type": "Actinoid",
        "pos": (7, 18.2)
    },
    "Rf": {
        "symbol": "Rf",
        "nNum": 104,
        "name": "Rutherfordium",
        "weight": "(267.122)",
        "type": "Transition Metal",
        "pos": (7, 4)
    },
    "Db": {
        "symbol": "Db",
        "nNum": 120,
        "name": "Dubnium",
        "weight": "(268.127)",
        "type": "Transition Metal",
        "pos": (7, 5)
    },
    "Sg": {
        "symbol": "Sg",
        "nNum": 106,
        "name": "Seaborgium",
        "weight": "(271.133)",
        "type": "Transition Metal",
        "pos": (7, 6)
    },
    "Bh": {
        "symbol": "Bh",
        "nNum": 107,
        "name": "Bohrium",
        "weight": "(272.138)",
        "type": "Transition Metal",
        "pos": (7, 7)
    },
    "Hs": {
        "symbol": "Hs",
        "nNum": 108,
        "name": "Hassium",
        "weight": "(270.150)",
        "type": "Transition Metal",
        "pos": (7, 8)
    },
    "Mt": {
        "symbol": "Mt",
        "nNum": 109,
        "name": "Meitnerium",
        "weight": "(278.170)",
        "type": "Transactinide",
        "pos": (7, 9)
    },
    "Ds": {
        "symbol": "Ds",
        "nNum": 110,
        "name": "Darmstadtium",
        "weight": "(281.175)",
        "type": "Transactinide",
        "pos": (7, 10)
    },
    "Rg": {
        "symbol": "Rg",
        "nNum": 111,
        "name": "Roentgenium",
        "weight": "(282.178)",
        "type": "Transactinide",
        "pos": (7, 11)
    },
    "Cn": {
        "symbol": "Cn",
        "nNum": 112,
        "name": "Copernicium",
        "weight": "(285.185)",
        "type": "Transactinide",
        "pos": (7, 12)
    },
    "Nh": {
        "symbol": "Nh",
        "nNum": 113,
        "name": "Nihonium",
        "weight": "(286.190)",
        "type": "Superactinide",
        "pos": (7, 13)
    },
    "Fl": {
        "symbol": "Fl",
        "nNum": 114,
        "name": "Flerovium",
        "weight": "(289.198)",
        "type": "Superactinide",
        "pos": (7, 14)
    },
    "Mc": {
        "symbol": "Mc",
        "nNum": 115,
        "name": "Moscovium",
        "weight": "(290.200)",
        "type": "Superactinide",
        "pos": (7, 15)
    },
    "Lv": {
        "symbol": "Lv",
        "nNum": 116,
        "name": "Livermorium",
        "weight": "(293.210)",
        "type": "Superactinide",
        "pos": (7, 16)
    },
    "Ts": {
        "symbol": "Ts",
        "nNum": 117,
        "name": "Tennessine",
        "weight": "(294.216)",
        "type": "Superactinide",
        "pos": (7, 17)
    },
    "Og": {
        "symbol": "Og",
        "nNum": 118,
        "name": "Oganesson",
        "weight": "(294.220)",
        "type": "Noble Gas",
        "pos": (7, 18)
    },
    "6": {
        "symbol": "6",
        "nNum": None,
        "name": None,
        "weight": None,
        "type": "Lanthanoid",
        "pos": (8, 3)
    },
    "7": {
        "symbol": "7",
        "nNum": None,
        "name": None,
        "weight": None,
        "type": "Actinoid",
        "pos": (9, 3)
    }
}

colors = {
    'Alkali Metal': '#6c3b01',
    'Alkaline Earth Metal': '#846011',
    'Lanthanoid': '#402c17',
    'Actinoid': '#732e4c',
    'Transition Metal': '#711019',
    'Post-Transition Metal': '#003666',
    'Metalloid': '#015146',
    'Reactive Non-Metal': '#3e6418',
    'Unstable': '#222',
    'Noble Gas': '#3a2151',
    'Filler': '#00b'
}
classes = {
    '57-71': 'top',
    '79-103': 'middle',
    '6': 'middle',
    '7': 'bottom'
}


class QtPeriodicTable(QMainWindow):

    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowType = ..., index: QModelIndex = None) -> None:
        self.gui = parent
        super(QtPeriodicTable, self).__init__(parent)
        self.setWindowTitle('Periodic Table')
        self.setObjectName('periodicTable')
        self.move(self.gui.pos())

        self.proxyWidget = QWidget()
        self.grid = SquareGrid()
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.infoLabel = QLabel()
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode = 'n-g'

        modeLayout = QVBoxLayout()
        self.modeWidget = AnimatedToggle()
        self.modeWidget.clicked.connect(self.modeChange)
        self.modeWidget.setMaximumWidth(50)
        self.modeText = QLabel('n-g')
        self.modeText.setAlignment(Qt.AlignmentFlag.AlignTop)

        modeLayout.addWidget(self.modeWidget, Qt.AlignmentFlag.AlignTop)
        modeLayout.addWidget(self.modeText, Qt.AlignmentFlag.AlignHCenter)

        self.grid.addLayout(modeLayout, 9, 1, Qt.AlignmentFlag.AlignTop)

        for i in range(1, 19):
            self.grid.setColumnStretch(i, 1)
            self.grid.addWidget(QLabel(f'{i}'), 0, i, Qt.AlignmentFlag.AlignCenter)
        for i in range(1, 8):
            self.grid.setRowStretch(i, 1)
            self.grid.addWidget(QLabel(f'{i}'), i, 0, Qt.AlignmentFlag.AlignHCenter)

        for info in periodic_table.values():
            if isinstance(info['pos'][1], float):
                row = 8 if str(info['pos'][1])[-1] == '1' else 9
            else:
                row = info['pos'][0]
            column = floor(info['pos'][1])
            info['zNum'] = None
            self.grid.addWidget(ElementCell(info, self), row, column, Qt.AlignmentFlag.AlignCenter)

        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(0)
        self.grid.setHorizontalSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

        self.setContentsMargins(0, 0, 0, 0)
        self.proxyWidget.setLayout(self.grid)
        self.setCentralWidget(self.proxyWidget)
        self.setStyleSheet("border: 0px; margin: 0px; padding: 0px;")

    def onSelect(self, cell: ElementCell) -> None:

        if cell.nNum is None:
            return

        spectraList: list[dict] = [interpName(item) for item in self.gui.spectraNames[1:]
                                   if f'{str(cell.nNum).rjust(2, "0")}-{cell.symbol}' in item]

        for item in [item for item in getLayoutWidgets(self.grid, ElementCell)
                     if item.objectName() == 'iso']:
            self.grid.removeWidget(item)

        if self.grid.itemAtPosition(1, 5) is not None:
            label = self.grid.itemAtPosition(1, 5).widget()
            self.grid.removeWidget(label)
            label.deleteLater()
        self.grid.setColumnStretch(5, 1)
        i, j = 1, 4

        spectraList = [item for item in spectraList if item['mode'] == 'n-g']
        if len(spectraList) == 0:
            self.infoLabel = QLabel("No Available Data")
            self.infoLabel.setObjectName('iso')
            self.grid.addWidget(self.infoLabel, 1, 5, 1, 2)

        for spectra in spectraList.copy():
            info = {}
            info['nNum'] = spectra['nNum']
            info['symbol'] = spectra['symbol']
            info['zNum'] = spectra['zNum']
            info['name'] = periodic_table[spectra['symbol']]['name']
            info['type'] = periodic_table[spectra['symbol']]['type']
            info['weight'] = periodic_table[spectra['symbol']]['weight']
            isoCell = ElementCell(info, parent=self)
            isoCell.zNum = spectra['zNum']
            isoCell.setObjectName('iso')
            margins = self.contentsMargins()
            height = int(self.window().sizeHint().height() + margins.top() + margins.bottom())
            color = colors.get(cell.type, '#222')
            isoCell.setStyleSheet(f"""
                *{{
                    padding: 0px;
                    margin: 0px;
                }}
                QWidget#cell, QWidget#Filler, #QWidget#iso{{
                    background-color: {color};
                    border: 1px solid #444;
                }}
                QLabel#Filler{{
                    font-size: {height // 120}pt;
                }}
                QWidget#cell:hover, QWidget#iso:hover{{
                    border: 1px solid #FFF;
                }}
                QLabel#nNum, QLabel#name, QLabel#weight{{
                    color: #DDD;
                    font-size: {height // 120}pt;
                    font-weight: 700;
                }}
                QLabel#symbol{{
                    color: #FFF;
                    font-size: {height // 80}pt;
                    font-weight: 800;
                }}
                """)
            self.grid.addWidget(isoCell, i, j, Qt.AlignmentFlag.AlignCenter)
            j += 1
            if j == 12:
                j = 4
                i += 1

    def isoSelect(self, cell: ElementCell) -> None:
        info = {'zNum': cell.zNum, 'symbol': cell.symbol, 'nNum': cell.nNum, 'mode': self.mode}

        self.gui.combobox.setCurrentText(constructName(info))
        self.close()

    def modeChange(self) -> None:
        if self.modeWidget.isChecked():
            self.modeText.setText('n-tot')
            self.mode = 'n-tot'
        else:
            self.modeText.setText('n-g')
            self.mode = 'n-g'
