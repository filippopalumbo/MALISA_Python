from enum import Enum, auto

class Tug_State(Enum):
    prep = auto()
    stand = auto()
    walk1 = auto()
    turn1 = auto()
    walk2 = auto()
    turn2 = auto()
    sit = auto()
    heel = auto()
    foot = auto()
    #toe = auto()