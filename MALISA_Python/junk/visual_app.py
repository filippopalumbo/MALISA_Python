import duckdb
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
import pandas as pd

# read csv files and translate epoch to human time, rename column to timestamp
def read_file(filename):
    data = duckdb.sql(f"""
SELECT
    to_timestamp(Timestamp) as timestamp,
    * EXCLUDE(Timestamp),
FROM read_csv('{filename}')
""").df()
    return data

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
            
    return f'{round(cop_x)},{round(cop_y)}'

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_file(file_path):
    df = read_file(file_path)

    # convert dataframe to a numpy array and reshape to pressure mat dimension
    data_array = df.set_index('timestamp').to_numpy().reshape(len(df), 80, 28)

    return data_array

def main():
    data = load_file('MALISA_Python/data/DS_TUG_Floor1.csv')

    # clear data of values below treshold
    data[data < 400] = 0

    mode = st.selectbox(label='Select display mode', options=['Single frame', 'Max of frames (view a full gait cycle)'])

    if mode == 'Single frame':
        i = st.slider('Choose frame', 0, len(data))
        image = data[i, :, :]
        distance_y, distance_x = calc_distance(image)
        info = [('total pressure', calc_total_pressure(image)), ('total area', calc_area(image)), ('y distance', distance_y), ('x distance', distance_x), ('center of pressure (x,y)', calc_cop(image))]
        df_info = pd.DataFrame(info, columns=['Metric', 'Value'])
        st.table(df_info)

    if mode == 'Max of frames (view a full gait cycle)':
        j, k = st.slider('Choose frames', 0, len(data),(1, 100),)
        image = data[j:k, :, :].max(axis=0)

    fig = go.Figure(data=go.Heatmap(z=image, zmin=0, zmax=2500, colorscale='Plasma'))
    fig.layout.height = 800
    fig.layout.width = 280
    fig.update(layout_showlegend=False)
    st.plotly_chart(fig)

main()
