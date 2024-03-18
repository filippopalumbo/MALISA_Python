import csv
import os
import uuid

def create_unique_filepath(initials):
    while True:
        # Generate a unique identifier
        unique_id = str(uuid.uuid4().hex)[:6]  # Get the first 6 characters of a random hexadecimal string 
        
        # Create the filepath
        filepath = f"tug_{initials}_{unique_id}.csv"
        
        # Check if the filepath already exists
        if not os.path.exists(filepath):
            break  # Exit the loop if the filepath is unique

    return filepath

def create_csv_file(filepath):
    # Create a new csv file containg data from test and person 
    # maybe generate a unique ID for each file? 
    # Define CSV file headers
    headers = ["timestamp", "event", "COP_x", "COP_y", "total_pressure", "total_area"]  
    
    if os.path.exists(filepath):
        raise FileExistsError("File already exists.")
    
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    print("Data written to CSV file successfully")
    

def write_to_csv(filepath, timestamp, event, COP_x, COP_y, total_pressure, total_area ):
    # Check if the file exists, if not, create it with headers
    if not os.path.exists(filepath):
       create_csv_file(filepath)
    
    # Write data to CSV file
    with open(filepath, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event, COP_x, COP_y, total_pressure, total_area])

def get_event_data(filepath, event):
    # List to store event data
    event_data = []

    # Read data from CSV file
    with open(filepath, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header row
        for row in reader:
            if row[1] == event:  # Check if event matches
                event_data.append(row)

    return event_data



# Example usage for function "get_event_data":
# filepath = "tug_test_DS_date.csv"
# event = "Walk1"
# data = get_event_data(filepath, event)
# print("Event data:")
# for row in data:
#     print(row)
        
# Example usage for function "write_to_csv":
# file_path = "tug_test_DS_date"
filepath = create_unique_filepath("DS")
write_to_csv(filepath, "2023-10-27 15:02:16.200000+02:00", "Walk1", 1, 1, 6000, 50)
print(filepath)