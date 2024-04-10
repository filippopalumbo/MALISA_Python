import pandas as pd
from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

def load_files(floor1_file_path, floor2_file_path, seat_file_path):
    floor1_df = pd.read_csv(floor1_file_path)
    floor2_df = pd.read_csv(floor2_file_path)
    seat_df = pd.read_csv(seat_file_path)

    floor1_array = floor1_df.iloc[:, 1:].to_numpy().reshape(len(floor1_df), 80, 28)
    floor2_array = floor2_df.iloc[:, 1:].to_numpy().reshape(len(floor2_df), 80, 28)
    seat_array = seat_df.iloc[:, 1:].to_numpy().reshape(len(seat_df), 20, 20)

    # Clear data of values below threshold 
    floor1_array[floor1_array < 400] = 0
    floor2_array[floor2_array < 400] = 0
    seat_array[seat_array < 100] = 0

    # Keep one df as a "timestamp list" - to retrieve timestamp on correct frame-index
    timestamp_list = floor1_df

    return timestamp_list, floor1_array, floor2_array, seat_array

def get_file_paths(test):

    if test == 'test 1':
        file_path_mat1 = 'MALISA_Python/data/tug1_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug1_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug1_seat.csv'
    if test == 'test 2':
        file_path_mat1 = 'MALISA_Python/data/tug2_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug2_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug2_seat.csv'
    if test == 'test 3':
        file_path_mat1 = 'MALISA_Python/data/tug3_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug3_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug3_seat.csv'
    if test == 'test 4':
        file_path_mat1 = 'MALISA_Python/data/tug4_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug4_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug4_seat.csv'  

    return file_path_mat1, file_path_mat2, file_path_seat 

def calculate_metrics(floor_frames, seat_frame):
    metrics = {}
    
    # Calculate and store metrics in dictionary
    metrics['cop_x'], metrics['cop_y'], metrics['mat_nr'] = calc_cop(floor_frames)
    metrics['total_pressure'] = calc_total_pressure(floor_frames)
    metrics['seat_total_pressure'] = calc_total_pressure(seat_frame)
    metrics['max_pressure'], metrics['x_cord_max_pressure'] = find_max_pressure(floor_frames)
    metrics['pressure_area'] = calc_area(floor_frames)
    metrics['y_distance'] = calc_y_distance(floor_frames)
    
    return metrics

def create_heatmaps_and_plot(floor1_frame, floor2_frame, seat_frame):
    # Create subplots for both floor mats and seat mat
    fig = make_subplots(rows=1, cols=3, column_widths=[200, 280, 280], row_heights=[800])

    # 12 bits gives a resolution of 4096 values, including 0 -> 4095
    fig.add_trace(go.Heatmap(z=seat_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=floor1_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=2)
    fig.add_trace(go.Heatmap(z=floor2_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=3)

    # Update layout
    fig.layout.height = 800
    fig.layout.width = (280 * 2) + 200
    # Adjust the heights of specific rows
    fig.update_layout(
        yaxis1=dict(domain=[0, 200/800]),  # Adjust the height of the first row
        yaxis2=dict(domain=[0, 800/800]),  # Adjust the height of the second row
        yaxis3=dict(domain=[0, 800/800])   # Adjust the height of the third row
    )
    fig.update_layout(showlegend=False)

    # Show the plotly chart
    st.plotly_chart(fig)

def create_table(metrics):
    info = [('timestamp', metrics['timestamp'][:21]), ('cop X', metrics['cop_x']), ('cop Y', metrics['cop_y']), ('mat nr', metrics['mat_nr']), ('seat total pressure', metrics['seat_total_pressure']), ('floor maximum pressure', metrics['max_pressure']), ('Y distance', metrics['y_distance']), ('X-cord (max pres.)', metrics['x_cord_max_pressure'])]
    info = pd.DataFrame(info, columns=['Metric', 'Value'])
    st.table(info)

def main():

    test = st.selectbox(label='Select TUG test', options=['test 1', 'test 2', 'test 3', 'test 4'])

    file_path_mat1, file_path_mat2, file_path_seat = get_file_paths(test)
    
    # Load data for sensor floor mats
    timestamp_list, floor1_array, floor2_array, seat_array = load_files(file_path_mat1, file_path_mat2, file_path_seat)

    index = st.slider('Choose frame', 0, len(timestamp_list)-1)

    floor1_frame = floor1_array[index, :, :]
    floor2_frame = floor2_array[index, :, :]
    seat_frame = seat_array[index, :, :] 

    # Create dictionary with metrics
    metrics = calculate_metrics([floor1_frame, floor2_frame], seat_frame)
    metrics['timestamp'] = timestamp_list.loc[index, 'timestamp']

    create_table(metrics)

    create_heatmaps_and_plot(floor1_frame, floor2_frame, seat_frame)


main()