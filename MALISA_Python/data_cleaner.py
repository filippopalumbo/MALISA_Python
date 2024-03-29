"""
Summary:
This module primarily focuses on cleaning and correcting data within a CSV file containing Tug events

Purpose:
Purpose is to ensure data accuracy, improve consistency, both crucial for any analysis or decicion-making 
based on the data to obtain reliable insights. By enhancing data quality we also optimize storage.

Contents:
list methods...

Usage:
Identify and correct mistakes, such as mislabeled data. 

Author: [Malin Ramkull & Hedda Eriksson]
Date: [2024-03-29]
"""

from csv_handler import*
from collections import defaultdict
from enumerations.tug_events import *


def clean_gait_events():
    # each scenario is explained in the bottom of this module.
    # TODO send filepath as a parameter perhaps? 
    filepath = "MALISA_Python/tug_event_data/tug_DS_test2.csv"
    data = read_csv_data(filepath)
    cleaned_data = []
    event = None
    previous_event = None
    next_event = None
    row = 0
    step = 0

    while row < len(data):
        event = Tug_Event(data[row]['event'])
        #breakpoint()
        if (row < (len(data)-1)):
            next_event = Tug_Event(data[row+1]['event'])
        # Scenario 1
        if (event == Tug_Event.start or event == Tug_Event.stand or event == Tug_Event.walk1 or event == Tug_Event.walk2 or event == Tug_Event.turn1 
            or event == Tug_Event.turn2 or event == Tug_Event.sit or event == Tug_Event.end):
            # Add row in data to cleaned_data
            cleaned_data.append(data[row])
            step = 1
        # Scenario 2 heel
        elif (event == Tug_Event.heel and (previous_event == Tug_Event.walk1 or previous_event == Tug_Event.walk2 or previous_event == Tug_Event.toe)):
            cleaned_data.append(data[row])
            step = 1
        # Scenario 3 heel - no heel exists
        elif(event == Tug_Event.foot and (previous_event == Tug_Event.walk1 or previous_event == Tug_Event.walk2 or previous_event == Tug_Event.toe)):
            data[row]['event'] = Tug_Event.heel # modify data foot event -> heel event
            cleaned_data.append(data[row])
            step = 1
        # Scenario 4 heel - one or more heels exists 
        elif(previous_event == Tug_Event.foot and event == Tug_Event.heel and (next_event == Tug_Event.heel or next_event == Tug_Event.foot)):
            cleaned_data.append(data[row])
            step = 1
        # Scenario 5 foot 
        elif(event == Tug_Event.foot and previous_event == Tug_Event.heel):
            i = row
            foot_data = []
            placement = Placement(data[row]['placement'])
            while (i < len(data) and Tug_Event(data[i]['event']) == Tug_Event.foot and Placement(data[i]['placement']) == placement):
                foot_data.append(data[i])
                i += 1
            
            last_row = len(foot_data)
            # Scenario 5.1 foot
            if (len(foot_data) > 1):
                toe = foot_data.pop() # remove toe from foot
                toe['event'] = Tug_Event.toe  # Modify data, foot event -> toe event
                cleaned_data.append(save_highest_pressure(foot_data))  # Save as foot
                cleaned_data.append(toe) # Save as toe
            #Scenario 5.2 foot
            else:
                toe_data = foot_data[0].copy()
                cleaned_data.append(foot_data[0])
                toe_data['event'] = Tug_Event.toe
                cleaned_data.append(toe_data) 

            event = Tug_Event.toe
            step = last_row # skip all next subsequent feet, they have been taking in to account in this scenario
                        
        row += step
        previous_event = Tug_Event(cleaned_data[len(cleaned_data)-1]['event']) 

    # TODO work some more on the saving function 
    filepath = "MALISA_Python/tug_event_data/2mod_tug_DS_test2.csv"
    write_csv_from_dict(filepath, cleaned_data)
    return cleaned_data


def save_highest_pressure(foot_data):
    highest_pressure_row = None
    max_pressure = float('-inf')  # Initialize with negative infinity

    for row in foot_data:
        total_pressure = float(row['total_pressure'])

        if total_pressure > max_pressure:
            max_pressure = total_pressure
            highest_pressure_row = row
    
   # cleaned_data.append(highest_pressure_row)
    return highest_pressure_row

# TODO
def control_placements():
    #control all placements (left and right) and correct errors

    return

def main():
    data = clean_gait_events()
    # print("Event data:")
    # for row in data:
    #     print(row)

main()


""" 
Scenario 1: if start, stand or walk1 just add to new modified data file

Scenario 2 heel: if previous event is walk1 and current event is heel, then add this as heel to new modified file. 
This makes sure we only save one heel(the first one) if there is one or more heel saved from tug state machine.

Scenario 3 heel: If tug state machine missed a heel, this will make the first footprint into a heel in th enew modified file.

Scenario 4 heel: If tug state machine saved one or more heels, save the first heel in the sequence.

Scenario 5 foot: seperates foot and toe
    Scenario 5.1 foot: if there is more then one foot event saved, clear out all except the foot with the highest pressure, 
    and the last foot in the subsequence as toe.
    Scenario 5.2 foot: if there is only one frame, dublicate and make one foot and one toe.
"""

