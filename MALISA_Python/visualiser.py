import pandas as pd
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

def create_table(parameters):
    tug_time_seconds = parameters['tug_time'].seconds + parameters['tug_time'].microseconds/1000000
    stand_up_time_seconds = parameters['stand_up_time'].seconds + parameters['stand_up_time'].microseconds/1000000
    turn_between_walks_time_seconds = parameters['turn_between_walks_time'].seconds + parameters['turn_between_walks_time'].microseconds/1000000
    turn_before_sit_time_seconds = parameters['turn_before_sit_time'].seconds + parameters['turn_before_sit_time'].microseconds/1000000

    table = [('TUG time', tug_time_seconds, 's'),
            ('Sit to Stand', stand_up_time_seconds, 's'),
            ('Mid Turning', turn_between_walks_time_seconds, 's'),
            ('End Turning Stand to Sit', turn_before_sit_time_seconds, 's'),
            ('Walk speed', parameters['walk_speed'], 'm/s'),
            ('Stride Length', parameters['stride_length'], 'cm')]

    table = pd.DataFrame(table, columns=['Parameter', 'Value' , 'Unit'])
    table['Value'] = table['Value'].round(2)

    return table

def create_heatmaps(floor1_frame, floor2_frame, seat_frame):
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

    return fig