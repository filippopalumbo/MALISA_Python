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
    x_cord_max_pressure = 0

    for frame in frames:
        current_max = frame.max() # Find the maximum value in the current DataFrame
        if current_max > max_pressure:
            max_pressure = current_max  # Update max_pressure if a greater value is found
            indices = np.where(frame == max_pressure) # Find the indices where the value occurs in the DataFrame
            # max_index = (indices[1][0], indices[0][0]) # X-and Y-coordinates
            x_cord_max_pressure = indices[1][0] # X-coordinate

    return max_pressure, x_cord_max_pressure

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
    total_pressure_frame1 = np.sum(frames[0])
    total_pressure_frame2 = np.sum(frames[1])

    if (total_pressure_frame1 == 0 and total_pressure_frame2 == 0):
        return 0,0,0
    elif (total_pressure_frame1 > 0 and total_pressure_frame2 == 0):
        return calc_cop_single_frame(frames[0], 1)
    elif (total_pressure_frame2 > 0 and total_pressure_frame1 == 0):
        return calc_cop_single_frame(frames[1], 2)
    elif (total_pressure_frame1 > 0 and total_pressure_frame2 > 0):
        return calc_cop_two_frames(frames[0], frames[1])

def calc_cop_single_frame(frame, mat):

    total_pressure = np.sum(frame)

    # Calculate the indices of the frame
    indices_y, indices_x = np.indices(frame.shape)

    # Calculate center of pressure
    cop_x = (np.sum(frame * indices_x) / total_pressure)
    cop_y = (np.sum(frame * indices_y) / total_pressure)
    
    return int(np.round(cop_x)), int(np.round(cop_y)), mat

def calc_cop_two_frames(frame1, frame2):

    frame1_total_pressure = np.sum(frame1)
    frame2_total_pressure = np.sum(frame2)    

    # Calculate the indices of each frame
    frame1_indices_y, frame1_indices_x = np.indices(frame1.shape)
    frame2_indices_y, frame2_indices_x = np.indices(frame2.shape)

    # Calculate center of pressure for each frame
    frame1_cop_x = (np.sum(frame1 * frame1_indices_x) / frame1_total_pressure)
    frame1_cop_y = (np.sum(frame1 * frame1_indices_y) / frame1_total_pressure)

    frame2_cop_x = (np.sum(frame2 * frame2_indices_x) / frame2_total_pressure)
    frame2_cop_y = (np.sum(frame2 * frame2_indices_y) / frame2_total_pressure)

    cop_x = (frame1_cop_x + (27-frame2_cop_x))/2

    cop_y = (frame1_cop_y + frame2_cop_y)/2

    mat = 1

    if(cop_y > frame1_cop_y):
        cop_y = frame2_cop_y-cop_y
        mat = 2

    if(cop_y < frame1_cop_y):
        cop_y = frame1_cop_y - cop_y

    return int(np.round(cop_x)), int(np.round(cop_y)), mat
 
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

def find_min_and_max_y_of_step(frames):
    # This method finds the highest(max) and lowest(min) y coordinate with a sensor value > 0,
    # Y coordinates pending between 79 as higest and 0 as lowest
    # In other terms, it finds the end and start of a foot or step.  
    # OBS. Works only with two frames
    min_y_of_step = [0,0]
    max_y_of_step = [0,0]

    nonzero_coords_frame_1 = np.transpose(np.nonzero(frames[0]))
    nonzero_coords_frame_2 = np.transpose(np.nonzero(frames[1]))
    if len(nonzero_coords_frame_1) > 0:
        max_y_coord_of_step = tuple(nonzero_coords_frame_1[-1])
        min_y_of_step = tuple(nonzero_coords_frame_1[0])
    elif len(nonzero_coords_frame_2) > 0:
        max_y_coord_of_step = tuple(nonzero_coords_frame_2[-1])
        min_y_of_step = tuple(nonzero_coords_frame_2[0])
    
    return min_y_of_step[0], max_y_of_step[0] # [0] to return only y-coord

