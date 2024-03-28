from enum import Enum

class Tug_Event(Enum):
    heel = 1
    foot = 2
    toe = 3
    stand = 4
    sit = 5
    walk1 = 6
    walk2 = 7
    turn1 = 8
    turn2 = 9
    start = 10
    end = 11

class Placement(Enum):
    left = 1
    right = 2