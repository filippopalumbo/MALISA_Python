import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.animation import FuncAnimation

def calculate_cop(matrix):
    """Calculate the Center of Pressure (CoP) of the pressure matrix."""
    total_pressure = matrix.sum()
    if total_pressure == 0:
        return None  # Avoid division by zero in case of no pressure

    rows, cols = matrix.shape
    x_coords, y_coords = np.meshgrid(range(cols), range(rows))
    
    x_cop = (x_coords * matrix).sum() / total_pressure
    y_cop = (y_coords * matrix).sum() / total_pressure

    return x_cop, y_cop

# Replace with your CSV file path
# file_path = 'DS_TUG_Floor1'
file_path = 'DS_TUG_Floor1'

# Read the CSV file
data = pd.read_csv(file_path)

# Dimensions of the sensor mat on the chair
# num_rows = 20
# num_cols = 20

# Dimensions of the sensor mat on the floor
num_rows = 80
num_cols = 28

# Initialize the plot for visualization
plt.ion()
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((num_rows, num_cols)), cmap='hot', interpolation='nearest', vmin=0, vmax=2000)

cop_marker, = ax.plot([], [], 'bo')  # Blue circle marker for CoP

# Code to save the animation as video
## Function to update the figure for each frame
#def update(frame):
#    row = data.iloc[frame]
#    matrix_data = row[1:].values.reshape(num_rows, num_cols)
#    heatmap.set_data(matrix_data)
#    cop = calculate_cop(matrix_data)
#    if cop:
#        cop_marker.set_data(cop[0], cop[1])
#    return heatmap, cop_marker,
#
## Create the animation
#ani = FuncAnimation(fig, update, frames=range(len(data)), interval=100, blit=True)
#
## Save the animation
#ani.save('pressure_data_visualization.mp4', writer='ffmpeg', fps=10)

# Code to visualize data at 10Hz
for index, row in data.iterrows():
    # Exclude the first column (timestamp) and reshape the rest into a matrix
    matrix_data = row[1:].values.reshape(num_rows, num_cols)

    # Update the heatmap with the new matrix data
    heatmap.set_data(matrix_data)

    # Calculate and plot the center of pressure
    cop = calculate_cop(matrix_data)
    if cop:
        cop_marker.set_data(cop[0], cop[1])

    # Redraw the plot
    fig.canvas.draw()
    fig.canvas.flush_events()

    # Sleep time controls the update rate of the visualization
    time.sleep(0.1)