"""
Summary:
This Python script provides functionality to create unique file paths, create CSV files with specific headers, 
write data to CSV files, and retrieve data from CSV files.

Purpose:
The purpose of this module is to offer a versatile data saving handler that can be utilized across various 
applications for efficient management and storage of data in a generic manner.

Contents:

Usage:
Import this file into your Python script using 'from csv_handler import *' to create, read and write to a CSV file for data managment.

Author: [Malin Ramkull & Hedda Eriksson]
Date: [2024-03-27]
"""
import csv
import os
import uuid

def create_unique_filepath(initials):
    #  This function generates a unique filepath for a CSV file based on the provided initials.
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
    # This function creates a filepath for a CSV file based on the given initials and test number. 
    # It is specifically designed for creating filepaths for tug event data CSV files.
    if isinstance(test, str):
        if " " in test:
            test = test.replace(" ", "")

    filepath = f"MALISA_Python/tug_event_data/tug_{initials}_{test}.csv"

    return filepath

 
def create_csv_file(filepath):
    # This function creates a new CSV file with the specified filepath.
    # Define (new) CSV file's header: | timestamp | event | COP x | COP y | total pressure |
    csvHeader = ["timestamp", "event","placement", "COP_x", "COP_y", "total_pressure"]  

    # Check if the filepath already exists, if it does, return filepath
    if os.path.exists(filepath):
        # print("CSV file already exist")
        return filepath 
    
    # Create new CSV file
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csvHeader)
        
    # print("CSV file successfully created")
    return filepath


def create_csv_sensor_data(filepath, rows, cols):
    # This function is designed to create a CSV file with a specific header based on the number of rows and columns provided. 
    # It is specifically designed for for sensor data (seating and floor) CSV files.
    if os.path.exists(filepath):
        # print("CSV file already exist")
        return filepath 
    
    # Create new CSV file
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write CSV header
        csvHeader = ["timestamp"]
        for row in range(rows):
            for column in range(cols):
                csvHeader.append("({row}-{column})".format(row=row, column=column))        
        writer.writerow(csvHeader)
    # print("CSV file successfully created")

    return filepath
        

def write_sensor_data(filepath, line):
    with open(filepath, mode="a", newline="") as file:  
        writer = csv.writer(file)
        writer.writerow(line)
        

def write_csv_from_dict(filepath, data):
    # This function writes data stored as dictionaries to a CSV file specified by the filepath. 
    # It writes the data in a tabular format where each dictionary corresponds to a row in the CSV file.
    headers = data[0].keys()
    with open(filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def write_to_csv(filepath, timestamp, event, placement,COP_x, COP_y, total_pressure):
    # This function writes data to a CSV file specified by the filepath.
    # It is specifically designed for for tug event data CSV files.

    # Write data to CSV file
    with open(filepath, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event, placement,COP_x, COP_y, total_pressure])


def read_csv_data(filepath):
    # This function reads data from a CSV file specified by the filepath and returns it as a list 
    # of dictionaries, where each dictionary represents a row in the CSV file with column names as keys.
    data = []

    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)

    return data


def get_csv_event(filepath, event):
    # List to store specific event data.
    event_data = []

    # Read data from CSV file
    with open(filepath, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row
        for row in reader:
            if row[1] == event:  # Check if event matches
                event_data.append(row)

    return event_data


def change_name(filepath, new_filepath):
    try:
        os.rename(filepath, new_filepath)
        print(f"File '{filepath}' renamed to '{new_filepath}' successfully.")
        # Delete the old file after renaming
        if os.path.exists(filepath):
            os.remove(filepath)
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
    except FileExistsError:
        print(f"File '{new_filepath}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")


def delete(filepath):
    # Check if the file exists before attempting to delete it
    if os.path.exists(filepath):
        # Delete the file
        os.remove(filepath)
