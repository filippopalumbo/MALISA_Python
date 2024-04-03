from enum import Enum

class Tug_Event(Enum):
    double_stance = 'Tug_Event.double_stance'
    heel = 'Tug_Event.heel'
    foot = 'Tug_Event.foot'
    toe = 'Tug_Event.toe'
    stand = 'Tug_Event.stand'
    sit = 'Tug_Event.sit'
    walk1 = 'Tug_Event.walk1'
    walk2 = 'Tug_Event.walk2'
    turn1 = 'Tug_Event.turn1'
    turn2 = 'Tug_Event.turn2'
    start = 'Tug_Event.start'
    end = 'Tug_Event.end'

class Placement(Enum):
    left = 'Placement.left'
    right = 'Placement.right'