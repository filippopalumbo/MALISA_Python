import numpy as np

def calc_total_pressure(image):
    total_pressure = image.sum()
    return total_pressure

def calc_area(image):
    #calculate the number of pixels where value > 0
    area = np.count_nonzero(image)
    return area

def calc_distance(image):

    distance_y = 0
    distance_x = 0

    # find coordinates of the first value > 0
    nonzero_coords = np.transpose(np.nonzero(image))
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
        distance_x = abs(last_coord[1] - first_coord[1])

    return distance_y, distance_x

def calc_cop(image):
    # calculate the indices of the image
    indices_x, indices_y = np.indices(image.shape)

    # calculate total pressure
    total_pressure = np.sum(image)

    # avoid division by zero
    if total_pressure == 0:
        return None
        
    # calculate center of pressure
    cop_x = np.sum(image * indices_x) / total_pressure
    cop_y = np.sum(image * indices_y) / total_pressure
            
    return round(cop_x), round(cop_y)
    #return f'{round(cop_x)},{round(cop_y)}'