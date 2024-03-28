"""
Summary:
This Python script provides functionality to create unique file paths, create CSV files with specific headers, 
write data to CSV files, and retrieve data from CSV files.

Purpose:
The purpose of this module is to offer a versatile data saving handler that can be utilized across various 
applications for efficient management and storage of data in a generic manner.

Contents:
- create_unique_filepath
- create_filepath
- create_csv_file
- write_to_csv
- read_csv_data
- get_csv_event 

Usage:
Import this file into your Python script using 'from csv_handler import *' to create, read and write to a CSV file for data managment.

Author: [Malin Ramkull & Hedda Eriksson]
Date: [2024-03-27]
"""
import csv
import os
import uuid

def create_unique_filepath(initials):
    while True:
        unique_id = str(uuid.uuid4().hex)[:4]  # Get the first 4 characters of a random hexadecimal string 
        
        # Create the filepath
        filepath = f"tug_{initials}_{unique_id}.csv"
        
        # Check if the filename is available by verifying the absence of a filepath with the same name.
        # If the filepath is unique, exit the loop.
        if not os.path.exists(filepath):
            break  

    return filepath

def create_filepath(initials, test):
    # Create filepath based on test number and initials
    if isinstance(test, str):
        if " " in test:
            test = test.replace(" ", "")

    filepath = f"MALISA_Python/tug_event_data/tug_{initials}_{test}.csv"

    return filepath


def create_csv_file(filepath):
    # Define (new) CSV file's header
    # | timestamp | event | COP x | COP y | total pressure |
    headers = ["timestamp", "event","placement", "COP_x", "COP_y", "total_pressure"]  
    # filepath = create_filepath(initials, test)

    # Check if the filepath already exists, if it does, return filepath
    if os.path.exists(filepath):
        print("CSV file already exist")
        return filepath 
    
    # Create new CSV file
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
    print("CSV file successfully created")
    return filepath
    

def write_to_csv(filepath, timestamp, event, placement,COP_x, COP_y, total_pressure):
    # Check if the file exists, if not, create it with headers
    # if not os.path.exists(filepath):
    #    create_csv_file(filepath)
    
    # Write data to CSV file
    with open(filepath, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event, placement,COP_x, COP_y, total_pressure])

# TODO
def read_csv_data(filepath):
    # List to store all data
    data = []

    # Read data from CSV file
    with open(filepath, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row
        for row in reader:
                data.append(row)

    return data

def get_csv_event(filepath, event):
    # List to store specific event data
    event_data = []

    # Read data from CSV file
    with open(filepath, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row
        for row in reader:
            if row[1] == event:  # Check if event matches
                event_data.append(row)

    return event_data


# EXAMPLE usage for function "get_csv_event":
    # filepath = "MALISA_Python/tug_event_data/tug_[initials]_[test].csv"
    # event = "Walk1"
    # data = get_event_data(filepath, event)
    # print("Event data:")
    # for row in data:
    #     print(row)
