import duckdb
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from frame_calculation import *

# read csv files and translate epoch to human time, rename column to timestamp
def read_file(filename):
    data = duckdb.sql(f"""
SELECT
    to_timestamp(Timestamp) as timestamp,
    * EXCLUDE(Timestamp),
FROM read_csv('{filename}')
""").df()
    return data

def resample_files(dfs):
    resampled_dfs = []
    for df in dfs:
        # set timestamp as index
        df.set_index('timestamp', inplace=True)
        # resample and set NaN to last recorded value value (forward fill)
        df_resampled = df.resample('100ms').mean().ffill()  # Change '100ms' to match your desired frequency (10 Hz)
        resampled_dfs.append(df_resampled)
    return resampled_dfs

# find the latest starttime 
def find_latest_start_time(dfs):
    latest_start_time = dfs[0].index.min()
    for df in dfs:
        df_min_date = df.index.min()
        if df_min_date > latest_start_time:
            latest_start_time = df_min_date
    return latest_start_time

def syncronize_start_time(dfs, start_time):
    syncronized_dfs = []
    for df in dfs:
        mask = df.index >= start_time
        df = df[mask]
        syncronized_dfs.append(df)
    return syncronized_dfs

def synchronize_end_time(df1, df2):
    if len(df1) > len(df2):
        df1 = df1.iloc[:len(df2)]  # Truncate df1 to match the length of df2
    elif len(df2) > len(df1):
        df2 = df2.iloc[:len(df1)]  # Truncate df2 to match the length of df1
    return df1, df2

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_file():
    df1 = read_file('MALISA_Python/data/DS_TUG_Floor1.csv')
    df2 = read_file('MALISA_Python/data/DS_TUG_Floor2.csv')
    df1, df2 = resample_files([df1, df2])
    start_time = find_latest_start_time([df1, df2])
    df1, df2 = syncronize_start_time([df1, df2], start_time = start_time)
    df1, df2 = synchronize_end_time(df1, df2)
    df1 = df1.to_numpy().reshape(len(df1), 80, 28)
    df2 = df2.to_numpy().reshape(len(df2), 80, 28)
     # special handling of floor2. Was this one places in the wrong direction?
    df2 = np.rot90(df2, 2, (1,2))
    concat_df = np.concatenate((df2, df1), axis=1)
    return concat_df

def main():

    data = load_file()

    # clear data of values below treshold
    data[data < 400] = 0

    mode = st.selectbox(label='Select display mode', options=['Single frame', 'Max of frames (view a full gait cycle)'])

    if mode == 'Single frame':
        i = st.slider('Choose frame', 0, len(data))
        image = data[i, :, :]
        distance_y, distance_x = calc_distance(image)
        info = [('total pressure', calc_total_pressure(image)), ('total area', calc_area(image)), ('y distance', distance_y), ('x distance', distance_x), ('center of pressure (x,y)', calc_cop(image))]
        info = pd.DataFrame(info, columns=['Metric', 'Value'])
        st.table(info)

    if mode == 'Max of frames (view a full gait cycle)':
        j, k = st.slider('Choose frames', 0, len(data),(1, 100),)
        image = data[j:k, :, :].max(axis=0)

    fig = go.Figure(data=go.Heatmap(z=image, zmin=0, zmax=2500, colorscale='Plasma'))
    #fig = go.Figure(data=go.Heatmap(z=image.T, zmin=0, zmax=2500, colorscale='Plasma')) // transpose image to make horizontal heatmap (update layout width/height)
    fig.layout.height = 1600
    fig.layout.width = 280
    fig.update(layout_showlegend=False)
    st.plotly_chart(fig)

main()
