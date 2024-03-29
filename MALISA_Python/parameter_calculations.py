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

def calc_tug_time(events):
    start = events.loc[events['event'] == 'Tug_Event.stand', 'timestamp'].iloc[0]
    end = events.loc[events['event'] == 'Tug_Event.sit', 'timestamp'].iloc[0]

    # Special handling for the test-files (time are of str-type, not epoch-type)
    start = str_to_epoch(start)
    end = str_to_epoch(end)
    
    # Calculate the time difference
    tug_time = end - start
    
    return tug_time

def str_to_epoch(str_time):
    if len(str_time) < 26:
        str_time = str_time[:-6]
        str_time += '.0'
    else:
        str_time = str_time[:-11]

    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"
    epoch_time = datetime.datetime.strptime(str_time, timestamp_format)
    return epoch_time

def calc_gait_parameters(events):
    # Split the dataframe at turn1 (to separate the walk1 ad walk2)

    # Find the index i of the row with the first heel-event
    # Save the placement p of row at the found index as current-state (left/right) 
    # Initialise a boolean for indicating if we are currently calc step and stride (1/0) = y/n

    # Iterate through each row (starting from the found index)
    # (if state=)
    # If the row i+1 -> event=foot & placement=p and row i+2 -> event=toe & placement=p
    #        A full step!
    #        calculate support-time -> toe-time - heel-time
    #        save cop for foot as step-length-start and stride-length-start
    # next-state = left
    #    
    #         

    """  
    # Count the number of instances where 'event' column has value 'Tug_Event.right_heel'
    # num_of_steps = (events['event'] == 'Tug_Event.right_heel').sum()
    
    # Find the index of the first row where 'event' column equals 'Tug_Event.right_heel'
    #index = events.index[events['event'] == 'Tug_Event.right_heel'].min()

    current_state = 'step-parameters'
    next_state = 'step-parameters'

    # Special handling for the test-files (time are of str-type, not epoch-type)
    heel_time = events.loc[index, 'timestamp']
    toe_time = events.loc[index, 'timestamp']

    heel_time = str_to_epoch(heel_time)
    toe_time = str_to_epoch(heel_time)

    # Iterate through events starting from the index of 'Tug_Event.right_heel'
    for i, row in events.iloc[index:].iterrows():
        return

    match current_state:

            case 'calc-step-parameters':
                if row['event'] == toe_event:
                    toe_time = events.loc[i, 'timestamp']
                    toe_time = str_to_epoch(toe_time)
                    step_time = toe_time-heel_time
                    
                if row['event'] == heel_event:
                    return"""


def main():
    events = pd.read_csv('MALISA_Python/tug_event_data/tug_DS_1.csv')
    breakpoint()
    # Convert timestamp column to datetime
    #events['timestamp'] = str_to_epoch(events['timestamp'])   
    events['timestamp'] = events['timestamp'].apply(str_to_epoch)
    breakpoint()
    tug_time = calc_gait_parameters(events)


main()