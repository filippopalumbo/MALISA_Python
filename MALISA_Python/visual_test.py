import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots
from calculations import *

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_files(file_paths):
    dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dfs.append(df.iloc[:, 1:].to_numpy().reshape(len(df), 80, 28))
    
    return dfs

def main():

    mode = st.selectbox(label='Select TUG test', options=['test 1', 'test 2', 'test 3', 'test 4'])

    if mode == 'test 1':
        file_path_mat1 = 'MALISA_Python/data/tug1_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug1_mat2.csv'
    if mode == 'test 2':
        file_path_mat1 = 'MALISA_Python/data/tug2_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug2_mat2.csv'
    if mode == 'test 3':
        file_path_mat1 = 'MALISA_Python/data/tug3_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug3_mat2.csv'
    if mode == 'test 4':
        file_path_mat1 = 'MALISA_Python/data/tug4_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug4_mat2.csv'

    dfs = load_files([file_path_mat1, file_path_mat2])
    
    # clear data of values below treshold
    for df in dfs:
        df[df < 400] = 0

    i = st.slider('Choose frame', 1, len(dfs[0])-1)
    
    frames = []
    for df in dfs:
        frames.append(df[i, :, :])

    cop_x, cop_y = calc_cop(frames)

    info = [('cop X', cop_x),('cop Y', cop_y)]
    info = pd.DataFrame(info, columns=['Metric', 'Value'])
    st.table(info)

    # Create subplots with one row and the number of columns equal to the number of frames
    fig = make_subplots(rows=1, cols=len(frames))

    # Add each heatmap to the corresponding subplot
    for i, frame in enumerate(frames, start=1):
       # if i == 2:
        #    frame = np.rot90(frame, 2)
        heatmap_trace = go.Heatmap(z=frame, zmin=0, zmax=2500, colorscale='Plasma')
        fig.add_trace(heatmap_trace, row=1, col=i)

    # Update layout
    fig.layout.height = 800
    fig.layout.width = 280 * len(frames)
    fig.update_layout(showlegend=False)

    # Show the plotly chart
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()