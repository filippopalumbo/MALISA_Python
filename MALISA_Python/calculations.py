import numpy as np
import pandas as pd

def calc_total_pressure(frames):
    total_pressure = 0
    for frame in frames:
        total_pressure += frame.sum() 
    
    return total_pressure

def find_max_pressure(frames):
    max_pressure = 0
    current_max = 0
    indices = 0
    max_index = None

    for frame in frames:
        current_max = frame.max() # Find the maximum value in the current DataFrame
        if current_max > max_pressure:
            max_pressure = current_max  # Update max_pressure if a greater value is found
            #indices = np.where(frame == max_pressure) # Find the indices where the value occurs in the DataFrame
            #max_index = (indices[0][0], indices[1][0])
    
     # Format the max_index for display
    # if mp_index is not None:
    #     max_index_str = f"[{mp_index[0]},{mp_index[1]}]"
    # else:
    #     max_index_str = "[N/A,N/A]"
            
    return max_pressure

def calc_area(frames):
    area = 0  # Initialize area

    # Calculate the area of sensor elements showing pressure
    for frame in frames:
        # Count the number of sensor elements with pressure > 0
        area += np.count_nonzero(frame)

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
 
def calc_y_distance(frames):
    total_pressure = 0

    total_pressure_frame1 = np.sum(frames[0])
    total_pressure_frame2 = np.sum(frames[1])

    if (total_pressure_frame1 == 0 and total_pressure_frame2 == 0):
        return total_pressure
    elif (total_pressure_frame1 > 0 and total_pressure_frame2 == 0):
        return calc_y_distance_single_frame(frames[0])
    elif (total_pressure_frame2 > 0 and total_pressure_frame1 == 0):
        return calc_y_distance_single_frame(frames[1])
    elif (total_pressure_frame1 > 0 and total_pressure_frame2 > 0):
        return (calc_y_distance_double_frame(frames[0], frames[1]))
    return 0

def calc_y_distance_double_frame(frame1, frame2):
    distance_y = 0
    nonzero_coords_frame1 = np.transpose(np.nonzero(frame1))
    nonzero_coords_frame2 = np.transpose(np.nonzero(frame2))

    # Find coordinate at mat1 value > 0 
    if len(nonzero_coords_frame1) > 0:
        mat1_coord = tuple(nonzero_coords_frame1[-1])
    # Find coordinate at mat2 value > 0 
    if len(nonzero_coords_frame2) > 0:
        mat2_coord = tuple(nonzero_coords_frame2[-1])
    if len(nonzero_coords_frame1) <= 0:
        mat1_coord = None
    if len(nonzero_coords_frame2) <= 0:
        mat1_coord = None
    
    # In this case both mat will be pending from zero, which means that the coordinate will be each mat's 
    # diff and one can just add the number together
    if mat1_coord is not None and mat2_coord is not None:
        distance_y = (mat1_coord[0] + mat2_coord[0])
    
    return distance_y

def calc_y_distance_single_frame(frame):
    distance_y = 0
    #distance_x = 0
    
    # find coordinates of the first value > 0
    nonzero_coords = np.transpose(np.nonzero(frame))
    if len(nonzero_coords) > 0:
        first_coord = tuple(nonzero_coords[0])
    else:
        first_coord = None

    # find coordinates of the last value > 0
    if len(nonzero_coords) > 0:
        last_coord = tuple(nonzero_coords[-1])
    else:
        last_coord = None
    
    # if both coordinates are found, calculate the distance between coordinates in x- resp. and y-axis
    if first_coord is not None and last_coord is not None:
        # calculate distance between coordinates in y-axis
        distance_y = abs(last_coord[0] - first_coord[0])
        # calculate distance between coordinates in x-axis
        #distance_x = abs(last_coord[1] - first_coord[1])

    return distance_y


