import pandas as pd
from calculations import *
from enum import Enum, auto
from MALISA_Python.enum.tug_states import Tug_State
from MALISA_Python.enum.tug_events import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

# Thresholds
threshold_seat = 3600
threshold_heal = 4000
threshold_y = 60
y_dis_low = 5
y_dis_high = 20

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
    pressure_on_seat = calc_total_pressure(frame)
    event = {}

    if(pressure_on_seat < threshold_seat):
        # If total pressure on seat is below threshold T_sit_to_stand then log event stand
        event = create_event_table(frame['timestamp'], Tug_Event.stand, 0, 0)
        return Tug_State.stand, event
    else:
        # Are we logging prep state?
        return Tug_State.prep 
    

def on_stand(metrics):
    current_tot_pressure = metrics['max_pressure']
    event = {}

    if(current_tot_pressure > threshold_heal):
        # If current total pressure is reaching max pressure threshold, 
        # then logg walk because it indicates first valid heel after standing position
        event = create_event_table(metrics['timestamp'], Tug_Event.walk1, metrics['cop_x'], metrics['cop_y'])
        return Tug_State.walk1, event
    else:
        # Else logg that we are still in stand state
        event = create_event_table(metrics['timestamp'], Tug_Event.stand, metrics['cop_x'], metrics['cop_y'])
        return Tug_State.stand, event


def on_walk(metrics, walk_nr):
    cop_y = metrics['cop_y']
    event = {}

    if(walk_nr == 1):
        if (cop_y > threshold_y):
            # Indicates that we are now turning around to start walking back
            event = create_event_table(metrics['timestamp'], Tug_Event.turn1, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.turn1, event
        else:
            # Still walking, estimate and log heel or foot
            event = estimate_gait(metrics, walk_nr)
            return Tug_State.walk1, event
    elif(walk_nr == 2):
        # On second walk (walk back)
        if(cop_y > threshold_y):
            # Indicates that we are now turning around to evantually sit down
            event = create_event_table(metrics['timestamp'], Tug_Event.turn2, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.turn2, event
        else:
            # Still walking, estimate and log heel or foot
            event = estimate_gait(metrics, walk_nr)
            return Tug_State.walk2, event


def on_turn(metrics, frame_seat, turn_nr):
    cop_y = metrics['cop_y']
    event = {}
    pressure_on_seat = calc_total_pressure(frame_seat)

    if(turn_nr == 1):
        # On first turn
        if(cop_y < threshold_y):
            # Indicates that we started walking again after turning
            event = create_event_table(metrics['timestamp'], Tug_Event.walk2, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.walk2, event
        else:
            # Still turning 
            event = create_event_table(metrics['timestamp'], Tug_Event.turn1, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.turn1, event
    elif(turn_nr == 2):
        # On second turn
        if(pressure_on_seat > threshold_seat):
            # Indicates that we are done turning and now sitting
            event = create_event_table(metrics['timestamp'], Tug_Event.sit, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.sit, event
        else:
            # Still turning 
            event = create_event_table(metrics['timestamp'], Tug_Event.turn2, metrics['cop_x'], metrics['cop_y'])
            return Tug_State.turn1, event


def on_sit(metrics):
    return 0

def estimate_gait(metrics, walk_nr):
    cop_x = metrics['cop_x']
    current_max_pressure = metrics['max_pressure']
    y_dis = metrics['y_distance']
    mat_nr = metrics['mat']
    event = {}
    placement = estimate_placement(walk_nr, mat_nr, cop_x)

    if(current_max_pressure > threshold_heal and (y_dis > y_dis_high or y_dis < y_dis_low)):
        if (placement == Placement.left):
            event = create_event_table(metrics['timestamp'], Tug_Event.left_heel, metrics['cop_x'], metrics['cop_y'])
        else:
            event = create_event_table(metrics['timestamp'], Tug_Event.right_heel, metrics['cop_x'], metrics['cop_y'])
        return event
    elif (1600 < current_max_pressure < 2900 and y_dis <= 12):
        if (placement == Placement.left):
            event = create_event_table(metrics['timestamp'], Tug_Event.left_foot, metrics['cop_x'], metrics['cop_y'])
        else:
            event = create_event_table(metrics['timestamp'], Tug_Event.right_foot, metrics['cop_x'], metrics['cop_y'])
        return event
    
def estimate_placement(walk_nr, mat, cop_x):

    if (walk_nr == 1 and mat == 1):
        if cop_x >= 14:
            return Placement.left
        elif cop_x < 14:
            return Placement.right
                
    elif (walk_nr == 1 and mat == 2):
        if cop_x >= 14:
            return Placement.right
        elif cop_x < 14:
            return Placement.left
        
    elif (walk_nr == 2 and mat == 2):
        if cop_x < 14:
            return Placement.right
        elif cop_x >= 14:
            return Placement.left
                
    elif (walk_nr == 2 and mat == 1):
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
    y_distance = calc_y_distance(frames)
    
    # Store metrics in the dictionary
    metrics['cop_x'] = cop_x
    metrics['cop_y'] = cop_y
    metrics['total_pressure'] = total_pressure
    metrics['max_pressure'] = max_pressure
    metrics['max_pressure_index'] = max_pressure_index
    metrics['pressure_area'] = pressure_area
    metrics['y_distance'] = y_distance
    metrics['mat'] = mat
    
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