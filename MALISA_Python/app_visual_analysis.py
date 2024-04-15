"""
Summary:
This Python script is designed as part of a Streamlit application for analyzing sensor data 
collected during the Timed Up and Go (TUG) test. It loads sensor data from floor mats and a 
seating mat, calculates various metrics related to pressure distribution and center of 
pressure, and visualizes the data using heatmaps and tables.

Purpose:
The purpose of this script is to provide a user-friendly interface for analyzing sensor 
data gathered during TUG tests. By loading sensor data from CSV files, calculating metrics, 
and visualizing the results, the script enables users to gain insights into the participants' 
movement patterns and pressure distribution during the test.

Usage:

Author: [Malin Ramkull & Hedda Eriksson]
Date: [10 april 2024]
"""
import pandas as pd
from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

def file_selector_sensor_data_floor_1(folder_path='./MALISA_Python/processed_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Fitness Mat 1', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_floor_2(folder_path='./MALISA_Python/processed_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Fitness Mat 2', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_seat(folder_path='./MALISA_Python/processed_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Seat Mat', filenames)
    return os.path.join(folder_path, selected_filename)

def load_files(floor1_file_path, floor2_file_path, seat_file_path):
    floor1_df = pd.read_csv(floor1_file_path)
    floor2_df = pd.read_csv(floor2_file_path)
    seat_df = pd.read_csv(seat_file_path)

    floor1_array = floor1_df.iloc[:, 1:].to_numpy().reshape(len(floor1_df), 80, 28)
    floor2_array = floor2_df.iloc[:, 1:].to_numpy().reshape(len(floor2_df), 80, 28)
    seat_array = seat_df.iloc[:, 1:].to_numpy().reshape(len(seat_df), 20, 20)

    # Clear data of values below threshold 
    floor1_array[floor1_array < 300] = 0
    floor2_array[floor2_array < 300] = 0
    seat_array[seat_array < 200] = 0

    # Special handling of seat for visualization purposes.
    seat_array = np.rot90(seat_array, 2, (1,2))

    # Rotate floor2 (the second floor mat is placed in opposite direction) 
    floor2_array = np.rot90(floor2_array, 2, (1,2))

    # Connect the separate floor mats to create the full walkway.
    floor_array = np.concatenate((floor2_array, floor1_array), axis=1)

    # Save one dataframe to keep the timestamps.
    timestamp_list = floor1_df

    return timestamp_list, floor_array, seat_array

def calculate_metrics(floor_frames, seat_frame):
    metrics = {}
    
    # Calculate and store metrics in dictionary
    metrics['cop_x'], metrics['cop_y'] = calc_cop(floor_frames)
    metrics['total_pressure'] = calc_total_pressure(floor_frames)
    metrics['seat_total_pressure'] = calc_total_pressure(seat_frame)
    metrics['max_pressure'], metrics['x_coord_max_pressure'], metrics['y_coord_max_pressure'] = calc_max_pressure(floor_frames)
    metrics['y_distance'], metrics['y_first_coord'], metrics['y_last_coord'] = calc_y_distance(floor_frames)
    metrics['left_side_total_pressure'], metrics['right_side_total_pressure'] = calc_separate_side_total_pressure(floor_frames)

    return metrics

def create_heatmaps_and_plot(floor_frame, seat_frame):
    # Create subplots for the walkway and seat 
    fig = make_subplots(rows=1, cols=2)

    # 12 bits gives a resolution of 4096 values, including 0 -> 4095
    fig.add_trace(go.Heatmap(z=seat_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=floor_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=2)

    # Update layout
    fig.update_layout(
        height=1200,  # Overall height
        width=600,  # Overall width
        xaxis1=dict(domain=[0, 0.4]),  # First subplot width
        xaxis2=dict(domain=[0.5, 1.0]),  # Second subplot width
        yaxis1=dict(domain=[0.85, 1]),  # First subplot height
        yaxis2=dict(domain=[0, 1]),  # Second subplot height
    )

    # Show the plotly chart
    st.plotly_chart(fig)


# def plot_floor(floor_frame):
#     fig = go.Figure(data=go.Heatmap(z=floor_frame, zmin=0, zmax=4095, colorscale='Plasma'))
#     fig.update_layout(height=1600, width=280)  # Update layout properties
#     st.plotly_chart(fig)

def create_table(metrics):
    info = [('timestamp', metrics['timestamp'][:21]), 
            ('cop X', metrics['cop_x']), 
            ('cop Y', metrics['cop_y']), 
            ('seat total pressure', metrics['seat_total_pressure']), 
            ('floor total pressure', metrics['total_pressure']), 
            ('floor maximum pressure', metrics['max_pressure']), 
            ('X maximum pressure', metrics['x_coord_max_pressure']),
            ('Y maximum pressure', metrics['y_coord_max_pressure']),
            ('Y distance', metrics['y_distance']), 
            ('Y first coord', metrics['y_first_coord']), 
            ('Y last coord', metrics['y_last_coord']), 
            ('left side tot pressure', metrics['left_side_total_pressure']), 
            ('right side tot pressure', metrics['right_side_total_pressure'])]
    info = pd.DataFrame(info, columns=['Metric', 'Value'])
    st.table(info)

def main():
    st.title('TUG Visual Analysis ')
    st.markdown('1. Ensure you have the necessary CSV files containing sensor data from the Timed Up and Go (TUG) test.')
    st.markdown('2. Use the file selectors below to choose the sensor data files.') 
    st.markdown('**Important:** It is crucial to pair the correct files. Otherwise, errors may occur.')
    st.markdown('3. Adjust the slider to choose the frame (timestamp) of interest for analysis.')

    file_floor_1 = file_selector_sensor_data_floor_1()
    file_floor_2 = file_selector_sensor_data_floor_2()
    file_seat = file_selector_sensor_data_seat()

    # Load data for sensor floor mats
    timestamp_list, floor_array, seat_array = load_files(file_floor_1, file_floor_2, file_seat)
    
    index = st.slider('Choose frame', 0, len(timestamp_list)-1)

    floor_frame = floor_array[index, :, :]
    seat_frame = seat_array[index, :, :] 

    # Create dictionary with metrics
    metrics = calculate_metrics(floor_frame, seat_frame)
    metrics['timestamp'] = timestamp_list.loc[index, 'timestamp']

    create_table(metrics)

    create_heatmaps_and_plot(floor_frame, seat_frame)


main()
