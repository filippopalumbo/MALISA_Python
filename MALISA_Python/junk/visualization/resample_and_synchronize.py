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

def load_files():
    # STEP 1 - resample and synchronize full tug recording (consists of 4 tug tests)
    #df1 = read_file('MALISA_Python/data/MB_TUG_Floor1.csv')
    #df2 = read_file('MALISA_Python/data/MB_TUG_Floor2.csv')
    #df3 = read_file('MALISA_Python/data/MB_TUG_Seat.csv')
    #df1, df2, df3 = resample_files([df1, df2, df3])
    #start_time = find_latest_start_time([df1, df2, df3])
    #df1, df2, df3 = syncronize_start_time([df1, df2, df3], start_time = start_time)
    #df1, df2 = synchronize_end_time(df1, df2)

    #df1.to_csv('MB_RES_SYN_Floor1.csv', index=True)
    #df2.to_csv('MB_RES_SYN_Floor2.csv', index=True)
    #df3.to_csv('MB_RES_SYN_Seat.csv', index=True)

    # STEP 2
    # Use visualization to identify what start- and end frame for each separate tug test

    # STEP 3 split the file into the separate tests at the correct start- and en frames
    df1 = pd.read_csv('MALISA_Python/data/RC_RES_SYN_Floor1.csv')
    df2 = pd.read_csv('MALISA_Python/data/RC_RES_SYN_Floor2.csv')
    df3 = pd.read_csv('MALISA_Python/data/RC_RES_SYN_Seat.csv')

    # TUG test 1
    # Slice the DataFrame using iloc
    sliced_df1 = df1.iloc[180:400, :]  # Slicing rows x and y, and all columns
    sliced_df2 = df2.iloc[180:400, :]  # Slicing rows x and y, and all columns
    sliced_df3 = df3.iloc[180:400, :]  # Slicing rows x and y, and all columns
    # Save sliced DataFrame to CSV 
    sliced_df1.to_csv('RC_tug1_floor1.csv', index=True)
    sliced_df2.to_csv('RC_tug1_floor2.csv', index=True)
    sliced_df3.to_csv('RC_tug1_seat.csv', index=True)

    # TUG test 2
    sliced_df1 = df1.iloc[960:1140, :]  # Slicing rows x and y, and all columns
    sliced_df2 = df2.iloc[960:1140, :]  # Slicing rows x and y, and all columns
    sliced_df3 = df3.iloc[960:1140, :]  # Slicing rows x and y, and all columns
    sliced_df1.to_csv('RC_tug2_floor1.csv', index=True)
    sliced_df2.to_csv('RC_tug2_floor2.csv', index=True)
    sliced_df3.to_csv('RC_tug2_seat.csv', index=True)

    # TUG test 3
    sliced_df1 = df1.iloc[1820:2050, :]  # Slicing rows x and y, and all columns
    sliced_df2 = df2.iloc[1820:2050, :]  # Slicing rows x and y, and all columns
    sliced_df3 = df3.iloc[1820:2050, :]  # Slicing rows x and y, and all columns
    sliced_df1.to_csv('RC_tug3_floor1.csv', index=True)
    sliced_df2.to_csv('RC_tug3_floor2.csv', index=True)
    sliced_df3.to_csv('RC_tug3_seat.csv', index=True)

    # TUG test 4
    sliced_df1 = df1.iloc[2520:2750, :]  # Slicing rows x and y, and all columns
    sliced_df2 = df2.iloc[2520:2750, :]  # Slicing rows x and y, and all columns
    sliced_df3 = df3.iloc[2520:2750, :]  # Slicing rows x and y, and all columns
    sliced_df1.to_csv('RC_tug4_floor1.csv', index=True)
    sliced_df2.to_csv('RC_tug4_floor2.csv', index=True)
    sliced_df3.to_csv('RC_tug4_seat.csv', index=True)

    return df1, df2, df3

    """
    # To visualize the two floor mats as one single catwalk
    df1, df2 = synchronize_end_time(df1, df2)
    df1 = df1.to_numpy().reshape(len(df1), 80, 28)
    df2 = df2.to_numpy().reshape(len(df2), 80, 28)
    df3 = df3.to_numpy().reshape(len(df3), 20, 20)

     # special handling of floor2, since concat shifts the coordinates
    df2 = np.rot90(df2, 2, (1,2))
    concat_df = np.concatenate((df2, df1), axis=1) """

def main():
    df1, df2, df3 = load_files()
    
    """
    data = load_files()

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
    st.plotly_chart(fig)"""

main()
