import pandas as pd
from enum import Enum, auto
from MALISA_Python.enum.tug_states import Tug_State

def load_files(file_path_mat1, file_path_mat2):
    df1 = pd.read_csv(file_path_mat1)
    df2 = pd.read_csv(file_path_mat2)

    return df1, df2

def on_prep():
    return 0

def on_stand():
    return 0

def on_walk(walk_nr):
    return 0

def on_turn(turn_nr):
    return 0

def on_sit():
    return 0

def calculate_metrics(frame1, frame2):
    cop = 0
    total_pressure = 0
    max_pressure = 0
    total_area = 0

    return cop, total_pressure, max_pressure, total_area
         

def main():
    mat1, mat2 = load_files("MALISA_Python/data/tug1_mat1.csv", "MALISA_Python/data/tug1_mat2.csv")

    index = 0
    current_state = Tug_State.prep

    while index < len(mat1):
        frame1 = mat1[index, :, :]
        frame2 = mat2[index, :, :]
        
        match current_state:
            case Tug_State.prep:
                next_state = on_prep()

            case Tug_State.stand:
                next_state = on_stand

            case Tug_State.walk1:
                next_state = on_walk(1)

            case Tug_State.turn1:
                next_state = on_turn(1)

            case Tug_State.walk2:
                next_state = on_walk(2)

            case Tug_State.turn2:
                next_state = on_turn(2)   
            
            case Tug_State.sit:
                next_state = on_sit()
        
        index += 1      

if __name__ == "__main__":
    main()