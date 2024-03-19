import numpy as np
import pandas as pd

def calc_total_pressure(dfs):
    total_pressure = 0
    for df in dfs:
        total_pressure += df.sum() 
    
    return total_pressure

def find_max_pressure(dfs):
    max_pressure = 0
    current_max = 0
    indices = 0
    max_index = None

    for df in dfs:
        current_max = df.max() # Find the maximum value in the current DataFrame
        if current_max > max_pressure:
            max_pressure = current_max  # Update max_pressure if a greater value is found
            indices = np.where(df == max_pressure) # Find the indices where the value occurs in the DataFrame
            max_index = (indices[0][0], indices[1][0])
    
    # # Format the max_index for display
    # if mp_index is not None:
    #     max_index_str = f"[{mp_index[0]},{mp_index[1]}]"
    # else:
    #     max_index_str = "[N/A,N/A]"
            
    return max_pressure, max_index

def calc_area(dfs):
    area = 0  # Initialize area

    # Calculate the area of sensor elements showing pressure
    for df in dfs:
        # Count the number of sensor elements with pressure > 0
        area += np.count_nonzero(df)

    # # Convert to actual area for the feets 
    # # Each sensor element has a size of 10 mm
    # area += (num_sensors_with_pressure * 10)
    # # Convert area from m^2 to cm^2
    # area_cm2 = (area / 100)
    
    return area

def calc_cop(frames):
    cop_x = 0
    cop_y = 0

    total_pressure = 0

    for frame in frames:
        total_pressure += np.sum(frame)

    if total_pressure == 0:
        return cop_x, cop_y

    for frame in frames:
        # calculate the indices of the image
        indices_y, indices_x = np.indices(frame.shape)

        # calculate total pressure
        total_pressure_frame = np.sum(frame)

        if total_pressure_frame  != 0:
            # calculate center of pressure
            cop_x += (np.sum(frame * indices_x) / total_pressure_frame)
            cop_y += (np.sum(frame * indices_y) / total_pressure_frame)
    
    return int(np.round(cop_x)), int(np.round(cop_y))



