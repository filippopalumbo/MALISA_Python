import pandas as pd
from calculations import *
from enum import Enum, auto
from MALISA_Python.enum.tug_states import Tug_State
from MALISA_Python.enum.tug_events import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

T_sit_to_stand = 3600
T_max_pressure = 4000

def load_seat_files(seat_file_path): 
    df = []
    df = pd.read_csv(seat_file_path)    
    return df

def load_files(file_paths):
    dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dfs.append(df.iloc[:, 1:].to_numpy().reshape(len(df), 80, 28))
    
    return dfs

def on_prep(frame):
    tot_pressure = calc_total_pressure(frame)

    if(tot_pressure < T_sit_to_stand):
        return Tug_State.stand
    else:
        return Tug_State.prep
    

def on_stand(metrics):
    current_tot_pressure = metrics['max_pressure']

    if(current_tot_pressure > T_max_pressure):
        return Tug_State.walk1
    else:
        return Tug_State.stand
    

def on_walk(metrics, walk_nr):
    return 0

def on_turn(metrics, turn_nr):
    return 0

def on_sit(metrics):
    return 0

def estimate_placement(walk, mat, cop_x):

    if (walk == Tug_Event.walk1 and mat == 1):
        if cop_x >= 14:
            return Placement.left
        elif cop_x < 14:
            return Placement.right
                
    elif (walk == Tug_Event.walk1 and mat == 2):
        if cop_x >= 14:
            return Placement.right
        elif cop_x < 14:
            return Placement.left
        
    elif (walk == Tug_Event.walk2 and mat == 2):
        if cop_x < 14:
            return Placement.right
        elif cop_x >= 14:
            return Placement.left
                
    elif (walk == Tug_Event.walk2 and mat == 1):
        if cop_x < 14:
            return Placement.left
        elif cop_x >= 14:
            return Placement.right
    
    return None

def calculate_metrics(frames):
    metrics = {}
    
    # Calculate metrics
    cop_x, cop_y, mat = calc_cop(frames)
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

def create_event_table(timestamp, event, cop_x, cop_y):
    event_table = {}

    event_table['timestamp'] = timestamp
    event_table['event'] = event
    event_table['cop_x'] = cop_x
    event_table['cop_y'] = cop_y

    return event_table


def main():
    mat1, mat2 = load_files(["MALISA_Python/data/tug1_mat1.csv", "MALISA_Python/data/tug1_mat2.csv"])
    # Load seat data
    seat = load_seat_files("MALISA_Python/MALISA_Python/data/tug1_seat.csv")

    index = 0
    current_state = Tug_State.prep


    while index < len(mat1):
        frame1 = mat1[index, :, :]
        frame2 = mat2[index, :, :]
        frame_seat = seat[index, :, :] 

        # Create dictionary with metrics
        metrics = calculate_metrics([frame1, frame2])

        # How to retrieve values from dictionary
        # cop_x = metrics_hash_table['cop_x'])  

        ###############VISUALS########################
        fig = make_subplots(rows=1, cols=3)
        ##############################################

        match current_state:

            case Tug_State.prep:
                next_state, event_table = on_prep(frame_seat)

            case Tug_State.stand:
                next_state, event_table = on_stand(metrics)

            case Tug_State.walk1:
                next_state, event_table = on_walk(metrics, 1)

            case Tug_State.turn1:
                next_state, event_table = on_turn(metrics, 1)

            case Tug_State.walk2:
                next_state, event_table = on_walk(metrics, 2)

            case Tug_State.turn2:
                next_state, event_table = on_turn(metrics, 2)   
            
            case Tug_State.sit:
                next_state, event_table = on_sit(metrics)
        
        current_state = next_state
        index += 1      

if __name__ == "__main__":
    main()