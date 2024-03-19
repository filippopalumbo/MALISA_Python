import numpy as np

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



