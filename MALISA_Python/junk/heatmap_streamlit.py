import duckdb
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

# read csv files and translate epoch to human time, rename column to timestamp
def read_file(filename):
    data = duckdb.sql(f"""
SELECT
    to_timestamp(Timestamp) as timestamp,
    * EXCLUDE(Timestamp),
FROM read_csv('{filename}')
""").df()
    return data

@st.cache_resource(
    show_spinner=" Loading data...",
)
def load_file(file_path):
    df = read_file(file_path)
    data_array = df.set_index('timestamp').to_numpy().reshape(len(df), 80, 28)

    return data_array

def main():
    data = load_file('MALISA_Python/data/DS_TUG_Floor1.csv')
    plt.ion()
    fig, ax = plt.subplots()
    heatmap = ax.imshow(np.zeros((80, 28)), cmap='hot', interpolation='nearest', vmin=0, vmax=2000)

    mode = st.selectbox(label='Select display mode', options=['Single frame', 'Max of frames'])
    if mode == 'Single frame':
        i = st.slider('Choose frame', 0, len(data), step=1)
        image = data[i, :, :]

    if mode == 'Max of frames':
        j, k = st.slider(
            'Choose frames',
            0, len(data),
            (1, 100),
        )
        image = data[j:k, :, :].max(axis=0)

    heatmap.set_data(image)
    st.write(fig)

main()