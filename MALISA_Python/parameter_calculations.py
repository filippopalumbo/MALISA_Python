"""
Summary:
This Python script contains functions to perform various operations in order to calculate the 
following gait parameters.
- Step Lenght
- Stride Length
- Swing duration
- Stance duration
- Step Count -> Gait velocity
- Golden Ratio! (duration measure)
...

Purpose:
The purpose of this module is to provide a library of operations that can be imported and used
as the final computational step in the TUG analysis process. 

Contents:
list methods...

Usage:
Import this file into your Python script using 'import gait_parameter_calculations'.
Using the output from the script "state_machine_tug" (a csv-file containing a list of 
logged events from a TUG test), you can then call the functions provided in this file to 
calculate gait parameters.

Author: [Malin Ramkull & Hedda Eriksson]
Date: [Date of creation or last modification]
"""
# TODO
# Reliability - mat 

import pandas as pd
import datetime
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *

WALKWAY_LENGTH = 6.4

# TUG parameters
def calc_tug_time(events):
    start = events.loc[events['event'] == 'Tug_Event.stand', 'timestamp'].iloc[0]
    end = events.loc[events['event'] == 'Tug_Event.sit', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    start = str_to_epoch(start)
    end = str_to_epoch(end)
    
    # Calculate the time difference
    tug_time = end - start
    
    return tug_time

def calc_stand_up_time(events):
    return None

def calc_turn_between_walks_time(events):
    start = events.loc[events['event'] == 'Tug_Event.turn1', 'timestamp'].iloc[0]
    end = events.loc[events['event'] == 'Tug_Event.walk2', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    start = str_to_epoch(start)
    end = str_to_epoch(end)
    
    # Calculate the time difference
    turn_time = end - start
    
    return turn_time    

def calc_turn_before_sit_time(events):
    start = events.loc[events['event'] == 'Tug_Event.turn2', 'timestamp'].iloc[0]
    end = events.loc[events['event'] == 'Tug_Event.sit', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    start = str_to_epoch(start)
    end = str_to_epoch(end)
    
    # Calculate the time difference
    turn_time = end - start
    
    return turn_time

# Gait parameters (that measures mobility and balance)
def calc_walk_speed(events):
    walk1_start = events.loc[events['event'] == 'Tug_Event.walk1', 'timestamp'].iloc[0]
    walk1_end = events.loc[events['event'] == 'Tug_Event.turn1', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    walk1_start = str_to_epoch(walk1_start)
    walk1_end = str_to_epoch(walk1_end)
    
    # Calculate the time duration of the first walk
    walk1_time = walk1_end - walk1_start

    walk2_start = events.loc[events['event'] == 'Tug_Event.walk2', 'timestamp'].iloc[0]
    walk2_end = events.loc[events['event'] == 'Tug_Event.turn2', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    walk2_start = str_to_epoch(walk2_start)
    walk2_end = str_to_epoch(walk2_end)
    
    # Calculate the time difference
    walk2_time = walk2_end - walk2_start

    walk_time = walk1_time + walk2_time

    walk_speed = walk_time / 2 * WALKWAY_LENGTH

    return walk_speed

def stride_length(events):
    row = 0
    stride_length = 0
    nbrOfStrides = 0
    distance = 0
    stride_data = []
    previous_left_foot = None
    previous_right_foot = None
    placement = None

    while row < len(events):
        i = row
        foot_data = []

        # Save info about walk2 as an inticator for change
        if (Tug_Event(events[row]['event']) == Tug_Event.walk2):
            stride_data.append(events[row])

        placement = events[row]['placement']
        
        # Find and save the foot with the highest pressure in the same subsequence
        while (i < len(events) and Tug_Event(events[i]['event']) == Tug_Event.foot and events[i]['placement'] == placement ): #and Placement(events[i]['placement']) == placement 
            foot_data.append(events[i])
            i += 1

        if (len(foot_data) > 0):
            stride_data.append(save_highest_pressure(foot_data))
            row += len(foot_data) # Skip the next foot events, they have been taken into account above.
        else:
            row += 1

    # Iterate through the foot data
    for data in stride_data:
        print()
        print(data)

        if (data['event'] == 'Tug_Event.walk2'):
            previous_left_foot = None
            previous_right_foot = None

        elif (data['placement'] == 'Placement.left'):
            current_left_foot = float(data['COP_y'])
            
            # Calculate distance if there's a previous left foot
            if previous_left_foot:
                print("distance left foot:")
                print(abs(current_left_foot - previous_left_foot))
                distance += abs(current_left_foot - previous_left_foot)
                nbrOfStrides += 1
            # Update previous left foot
            previous_left_foot = current_left_foot

        elif (data['placement'] == 'Placement.right'):
            current_right_foot = float(data['COP_y'])
            
            # Calculate distance if there's a previous left foot
            if previous_right_foot:
                print("distance right foot:")
                print(abs(current_right_foot - previous_right_foot))
                distance += abs(current_right_foot - previous_right_foot)
                nbrOfStrides += 1
                # ebreakpoint()
            # Update previous left foot
            previous_right_foot = current_right_foot
    print("Strides:")
    print(nbrOfStrides)
    # Avoid divition by zero
    if(nbrOfStrides != 0):
        stride_length = distance / nbrOfStrides  

    return stride_length  
        

## ON HOLD (Inaccurate with heels and toes...)
def support_time():
    return None

def save_highest_pressure(event_data):
    highest_pressure_data = None
    max_pressure = float('-inf')  # Initialize with negative infinity

    for data in event_data:
        total_pressure = float(data['total_pressure'])

        if total_pressure > max_pressure:
            max_pressure = total_pressure
            highest_pressure_data = data
    
    return highest_pressure_data

def str_to_epoch(str_time):
    if len(str_time) < 26:
        str_time = str_time[:-6]
        str_time += '.0'
    else:
        str_time = str_time[:-11]

    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"
    epoch_time = datetime.datetime.strptime(str_time, timestamp_format)
    return epoch_time

def main():
    # events = pd.read_csv('MALISA_Python/tug_event_data/tug_DS_test1.csv')
    events = read_csv_data('MALISA_Python/tug_event_data/tug_DS_test4.csv')

    stride = stride_length(events)
    print(stride)
    # breakpoint()
    # Convert timestamp column to datetime
    # events['timestamp'] = str_to_epoch(events['timestamp'])   
    # events['timestamp'] = events['timestamp'].apply(str_to_epoch)

main()