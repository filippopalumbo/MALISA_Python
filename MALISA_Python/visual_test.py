import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots
from calculations import *

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_files(floor_file_paths, seat_file_path):
    dfs = []

    for file_path in floor_file_paths:
        df = pd.read_csv(file_path)
        # Dimensions of floor mat is 80 x 28
        dfs.append(df.iloc[:, 1:].to_numpy().reshape(len(df), 80, 28))

    # Dimensions of seat mat is 20 x 20
    seat = pd.read_csv(seat_file_path)
    dfs.append(seat.iloc[:, 1:].to_numpy().reshape(len(df), 20, 20))

    return dfs

def main():

    mode = st.selectbox(label='Select TUG test', options=['test 1', 'test 2', 'test 3', 'test 4'])

    if mode == 'test 1':
        file_path_mat1 = 'MALISA_Python/data/tug1_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug1_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug1_seat.csv'
    if mode == 'test 2':
        file_path_mat1 = 'MALISA_Python/data/tug2_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug2_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug2_seat.csv'
    if mode == 'test 3':
        file_path_mat1 = 'MALISA_Python/data/tug3_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug3_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug3_seat.csv'
    if mode == 'test 4':
        file_path_mat1 = 'MALISA_Python/data/tug4_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug4_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug4_seat.csv'

    dfs = load_files([file_path_mat1, file_path_mat2], file_path_seat)
    
    # Clear data of values below threshold for the first two DataFrames in dfs (aka the floor mats)
    for df in dfs[:-1]:
        df[df < 400] = 0

    i = st.slider('Choose frame', 0, len(dfs[0])-1)
    
    frames = []
    for df in dfs:
        frames.append(df[i, :, :])

    cop_x, cop_y, cop_mat = calc_cop(frames[:-1])
    y_distance = calc_y_distance(frames[:-1])
    area = calc_area(frames[:-1])
    tot_pressure = calc_total_pressure(frames[:-1])
    max_pressure = find_max_pressure(frames[:-1])


    floor_info = [('cop X', cop_x),('cop Y', cop_y), ('mat', cop_mat), ('tot area', area), ('tot pressure', tot_pressure), ('max pressure', max_pressure), ('y-distance', y_distance)]
    floor_info = pd.DataFrame(floor_info, columns=['Floor Metric', 'Value'])
    st.table(floor_info)

    tot_pressure = calc_total_pressure(frames[-1])
    max_pressure = find_max_pressure(frames[-1])
    seat_info = [('total pressure', tot_pressure), ('max pressure', max_pressure)]
    seat_info = pd.DataFrame(seat_info, columns=['Seat Metric', 'Value'])
    st.table(seat_info)

    # Create subplots with one row and the number of columns equal to the number of frames
    fig = make_subplots(rows=1, cols=len(frames))

    # Add each heatmap to the corresponding subplot
    for i, frame in enumerate(frames, start=1):
        heatmap_trace = go.Heatmap(z=frame, zmin=0, zmax=4095, colorscale='Plasma') # 12 bits gives a resolution of 4096 values, including 0 -> 4095 
        fig.add_trace(heatmap_trace, row=1, col=i)

    # Update layout
    fig.layout.height = 800
    fig.layout.width = 280 * len(frames)
    fig.update_layout(showlegend=False)

    # Show the plotly chart
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()