import duckdb
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# read csv files and translate epoch to human time, rename column to timestamp
def read_file(filename):
    data = duckdb.sql(f"""
SELECT
    to_timestamp(Timestamp) as timestamp,
    * EXCLUDE(Timestamp),
FROM read_csv('{filename}')
""").df()
    return data

# find the latest starttime 
def find_latest_start_time(dfs, time_col='timestamp'):
    latest_start_time = dfs[0][time_col].min()
    for df in dfs:
        df_min_date = df[time_col].min()
        if df_min_date > latest_start_time:
            latest_start_time = df_min_date
    return latest_start_time

# 
def syncronize_start_time(dfs, start_time, time_col='timestamp'):
    syncronized_dfs = []
    for df in dfs:
        mask = df[time_col] >= start_time
        df = df[mask].set_index(time_col) # Set index to time_col, so that the dataframe consists of only heatmap values
        syncronized_dfs.append(df)
    return syncronized_dfs




def pad_and_concat(floor1, floor2, seat):
    max_nbr_frames = max(len(floor1), len(floor2), len(seat))
    floor1 = floor1.to_numpy().reshape(len(floor1), 80, 28)
    floor2 = floor2.to_numpy().reshape(len(floor2), 80, 28)
    seat = seat.to_numpy().reshape(len(seat), 20, 20)

    # calibrate by dividing each with its max
    #floor1 = floor1/floor1.max()
    #floor2 = floor2/floor2.max()
    #seat = seat/seat.max()

    # special handling of seat:
    side_padding = np.zeros((len(seat), 20, 4))
    seat = np.concatenate((side_padding, seat, side_padding), axis=2)
    
    # special handling of seat. Was this one places in the wrong direction?
    seat = np.rot90(seat, 2, (1,2))

    # special handling of floor2. Was this one places in the wrong direction?
    floor2 = np.rot90(floor2, 2, (1,2))

    padded_arrays = []
    for array in [floor1, floor2, seat]:
        nbr_missing_frames = max_nbr_frames - len(array)
        missing_frames = np.zeros((nbr_missing_frames, array.shape[1], array.shape[2]))
        array = np.concatenate((array, missing_frames))
        padded_arrays.append(array)


    floor1, floor2, seat = padded_arrays
    total_recording = np.concatenate((floor2, floor1, seat), axis=1)
    

    return total_recording


@st.cache_resource(
    show_spinner=" Cooking up recording...",
)
def load_recording():
    floor1 = read_file('MALISA_Python/data/DS_TUG_Floor1.csv')
    floor2 = read_file('MALISA_Python/data/DS_TUG_Floor2.csv')
    seat = read_file('MALISA_Python/data/DS_TUG_Seat2.csv')
    latest_start_time = find_latest_start_time([floor1, floor2, seat])
    floor1, floor2, seat = syncronize_start_time([floor1, floor2, seat], start_time=latest_start_time)
    total_recording = pad_and_concat(floor1, floor2, seat) # shape: (3339, 180, 28)
    return total_recording

def main():
    recording = load_recording()
    mode = st.selectbox(label='Select display mode', options=['Single frame', 'Max of frames'])
    if mode == 'Single frame':
        i = st.slider('Choose frame', 0, len(recording), step=1)
        image = recording[i:i+1, :, :].max(axis=0)
    if mode == 'Max of frames':
        j, k = st.slider(
            'Choose frames',
            0, len(recording),
            (1, 100),
        )
        image = recording[j:k, :, :].max(axis=0)
    fig = go.Figure(data=go.Heatmap(z=image))
    fig.layout.height = 1000
    fig.layout.width = 225
    fig.update(layout_showlegend=False)
    st.plotly_chart(fig)

main()