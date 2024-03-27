import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go  
from frame_calculation import *

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_file(file_path_mat1, file_path_mat2):
    df1 = pd.read_csv(file_path_mat1)
    df2 = pd.read_csv(file_path_mat2)
    
    df1 = df1.iloc[:, 1:].to_numpy().reshape(len(df1), 80, 28)
    df2 = df2.iloc[:, 1:].to_numpy().reshape(len(df2), 80, 28)

    # special handling of floor2. Was this one places in the wrong direction?
    df2 = np.rot90(df2, 2, (1,2))
    concat_df = np.concatenate((df2, df1), axis=1)
    
    return concat_df

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

    data = load_file(file_path_mat1, file_path_mat2)
    
    # clear data of values below treshold
    data[data < 400] = 0

    i = st.slider('Choose frame', 0, len(data)-1)
    image = data[i, :, :]
    distance_y, distance_x = calc_distance(image)
    info = [('total pressure', calc_total_pressure(image)), ('total area', calc_area(image)), ('y distance', distance_y), ('x distance', distance_x), ('center of pressure (x,y)', calc_cop(image))]
    info = pd.DataFrame(info, columns=['Metric', 'Value'])
    st.table(info)

    fig = go.Figure(data=go.Heatmap(z=image, zmin=0, zmax=2500, colorscale='Plasma'))
    #fig = go.Figure(data=go.Heatmap(z=image.T, zmin=0, zmax=2500, colorscale='Plasma')) // transpose image to make horizontal heatmap (update layout width/height)
    fig.layout.height = 1600
    fig.layout.width = 280
    fig.update(layout_showlegend=False)
    st.plotly_chart(fig)

main()
