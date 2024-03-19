import numpy as np
import pandas as pd

def calc_total_pressure(dfs):
    for df in dfs:
        total_pressure += df 
    
    return total_pressure

def find_max_pressure(dfs):
    max_pressure = 0 # Initialize with negative infinity to ensure any value will be greater
    
    for df in dfs:
        max_in_df = df.max().max()  # Find the maximum value in the current DataFrame
        if max_in_df > max_pressure:
            max_pressure = max_in_df  # Update max_pressure if a greater value is found
            max_index = df.stack().idxmax() # Index of max_pressure sensor

    return max_pressure, max_index

def calc_area(dfs):
    area = 0  # Initialize area
    
    # Calculate the area of sensor elements showing pressure
    for df in dfs:
        # Count the number of sensor elements with pressure > 0
        num_sensors_with_pressure = np.count_nonzero(df)
        # Assuming each sensor element has a size of 10 mm
        area += num_sensors_with_pressure * 10
    
    # Convert area from mm^2 to cm^2
    area_cm2 = area / 100
    
    return area_cm2


