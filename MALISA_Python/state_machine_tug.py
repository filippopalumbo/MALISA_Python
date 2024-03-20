import pandas as pd
from calculations import *
from enum import Enum, auto
from MALISA_Python.enum.tug_states import Tug_State

def load_files(file_paths):
    dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dfs.append(df.iloc[:, 1:].to_numpy().reshape(len(df), 80, 28))
    
    return dfs

def on_prep(metrics):
    return 0

def on_stand(metrics):
    return 0

def on_walk(metrics, walk_nr):
    return 0

def on_turn(metrics, turn_nr):
    return 0

def on_sit(metrics):
    return 0

def calculate_metrics(frames):
    metrics = {}
    
    # Calculate metrics
    cop_x, cop_y = calc_cop(frames)
    total_pressure = calc_total_pressure(frames)
    max_pressure, max_pressure_index = find_max_pressure(frames)
    pressure_area = calc_area(frames)
    
    # Store metrics in the dictionary
    metrics['cop_x'] = cop_x
    metrics['cop_y'] = cop_y
    metrics['total_pressure'] = total_pressure
    metrics['max_pressure'] = max_pressure
    metrics['max_pressure_index'] = max_pressure_index
    metrics['pressure_area'] = pressure_area
    
    return metrics

def main():
    mat1, mat2 = load_files(["MALISA_Python/data/tug1_mat1.csv", "MALISA_Python/data/tug1_mat2.csv"])

    index = 0
    current_state = Tug_State.prep


    while index < len(mat1):
        frame1 = mat1[index, :, :]
        frame2 = mat2[index, :, :]

        # Create dictionary with metrics
        metrics = calculate_metrics([frame1, frame2])

        # How to retrieve values from dictionary
        # cop_x = metrics_hash_table['cop_x'])  

        match current_state:

            case Tug_State.prep:
                next_state = on_prep(metrics)

            case Tug_State.stand:
                next_state = on_stand(metrics)

            case Tug_State.walk1:
                next_state = on_walk(metrics, 1)

            case Tug_State.turn1:
                next_state = on_turn(metrics, 1)

            case Tug_State.walk2:
                next_state = on_walk(metrics, 2)

            case Tug_State.turn2:
                next_state = on_turn(metrics, 2)   
            
            case Tug_State.sit:
                next_state = on_sit(metrics)
        
        current_state = next_state
        index += 1      

if __name__ == "__main__":
    main()