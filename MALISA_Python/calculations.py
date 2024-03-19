import numpy as np

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



