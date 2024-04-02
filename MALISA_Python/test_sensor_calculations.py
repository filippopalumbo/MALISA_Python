import numpy as np

def calc_total_pressure(frame):
    total_pressure = frame.sum()   
    return total_pressure

def calc_max_pressure(frame):
    max_pressure = frame.max()
    indices = np.where(frame == max_pressure) # Find the indices where the value occurs in the DataFrame
    # max_index = (indices[1][0], indices[0][0]) # X-and Y-coordinates
    x_cord_max_pressure = indices[1][0] # X-coordinate
    y_cord_max_pressure = indices[0][0]

    return max_pressure, x_cord_max_pressure, y_cord_max_pressure

def calc_cop(frame):
    total_pressure = np.sum(frame)
    
    # Avoid division by zero
    if total_pressure == 0:
        return 0,0

    # Calculate the indices of the frame
    indices_y, indices_x = np.indices(frame.shape)

    # Calculate center of pressure
    cop_x = (np.sum(frame * indices_x) / total_pressure)
    cop_y = (np.sum(frame * indices_y) / total_pressure)
    
    return int(np.round(cop_x)), int(np.round(cop_y))

def calc_y_distance(frame):
    distance_y = 0
    y_first_coord = 0
    y_last_coord = 0
    
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
        y_first_coord = first_coord[0]
        y_last_coord = last_coord[0]

    return distance_y, y_first_coord, y_last_coord

def calc_separate_side_total_pressure(frame):
    total_pressure = calc_total_pressure(frame)

    # Slice frame 1 to keep columns 1-14 (right side of walkway)
    right_side = frame[:, :14]    

    # Calculate total pressure of each side of the walkway
    total_pressure_right_side = right_side.sum() 
    total_pressure_left_side = total_pressure - total_pressure_right_side

    return total_pressure_left_side, total_pressure_right_side


