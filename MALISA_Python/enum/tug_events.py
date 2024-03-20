from enum import Enum

class Tug_Event(Enum):
    left_heel = 1
    left_foot = 2
    left_toe = 3
    right_heel = 4
    right_foot = 5
    right_toe = 6
    stand = 7
    sit = 8
    walk1 = 9
    walk2 = 10
    turn1 = 11
    turn2 = 12

class Direction(Enum):
    left = "left"
    right = "right"