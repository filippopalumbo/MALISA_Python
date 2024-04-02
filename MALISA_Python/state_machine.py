import pandas as pd
from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

# Thresholds
threshold_seat = 3600
threshold_heal = 2600
y_dis_low = 5
y_dis_high = 20
y_start_max = 60


def load_files(floor1_file_path, floor2_file_path, seat_file_path):
    floor1_df = pd.read_csv(floor1_file_path)
    floor2_df = pd.read_csv(floor2_file_path)
    seat_df = pd.read_csv(seat_file_path)

    floor1_array = floor1_df.iloc[:, 1:].to_numpy().reshape(len(floor1_df), 80, 28)
    floor2_array = floor2_df.iloc[:, 1:].to_numpy().reshape(len(floor2_df), 80, 28)
    seat_array = seat_df.iloc[:, 1:].to_numpy().reshape(len(seat_df), 20, 20)

    # Clear data of values below threshold 
    floor1_array[floor1_array < 500] = 0
    floor2_array[floor2_array < 500] = 0
    seat_array[seat_array < 100] = 0

    # special handling of seat. Was this one places in the wrong direction?
    seat_array = np.rot90(seat_array, 2, (1,2))
    # special handling of floor2. Placed in opposite direction
    floor2_array = np.rot90(floor2_array, 2, (1,2))
    floor_array = np.concatenate((floor2_array, floor1_array), axis=1)

    timestamp_list = floor1_df

    return timestamp_list, floor_array, seat_array

def on_prep(metrics, filepath_TED):
    seat_total_pressure = metrics['seat_total_pressure']
    
    if(seat_total_pressure < threshold_seat):
        # If total pressure on seat is below threshold T_sit_to_stand then log event stand
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.start, None, None, None, None)
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.stand, None, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.stand
    else:
        return Tug_State.prep
    
def on_stand(metrics, filepath_TED):
    y_distance = metrics['y_distance']

    if (y_distance > y_dis_high):
        # If current total pressure is reaching max pressure threshold, 
        # then logg walk because it indicates first valid heel after standing position
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.walk1, None,metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk1
    else:
        # Else logg that we are still in stand state
        return Tug_State.stand

def on_walk_1(metrics, filepath_TED):
    y_first_coord = metrics['y_first_coord']
    y_last_coord = metrics['y_last_coord']
    x_max_pressure = metrics['x_coord_max_pressure']
    y_max_pressure = metrics['y_coord_max_pressure']
    max_pressure = metrics['max_pressure']
    left_side_total_pressure = metrics['left_side_total_pressure']
    right_side_total_pressure = metrics['right_side_total_pressure'] 

    # The first walk during TUG (walking away from the chair)
    if (y_last_coord < 20):
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.turn1, None, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.turn1
    else:
        event = None
        placement = None
        distance_max_y_to_last_y = abs(y_max_pressure - y_last_coord)
        distance_max_y_to_first_y = abs(y_max_pressure - y_first_coord)
        if((max_pressure > threshold_heal) and (distance_max_y_to_first_y < distance_max_y_to_last_y)): 
            event = Tug_Event.heel
            if(x_max_pressure < 14):
                placement = Placement.right
            else:
                placement = Placement.left
        else:
            event = Tug_Event.foot

            if(right_side_total_pressure > left_side_total_pressure):
                placement = Placement.right
            else:
                placement = Placement.left
        write_to_csv(filepath_TED, metrics['timestamp'], event, placement, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk1

def on_walk_2(metrics, filepath_TED):
    y_first_coord = metrics['y_first_coord']
    y_last_coord = metrics['y_last_coord']
    x_max_pressure = metrics['x_coord_max_pressure']
    y_max_pressure = metrics['y_coord_max_pressure']
    max_pressure = metrics['max_pressure']
    left_side_total_pressure = metrics['left_side_total_pressure']
    right_side_total_pressure = metrics['right_side_total_pressure'] 

    if(y_first_coord > 140):
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.turn2, None ,metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.turn2
    else:
        event = None
        placement = None
        distance_max_y_to_last_y = abs(y_max_pressure - y_last_coord)
        distance_max_y_to_first_y = abs(y_max_pressure - y_first_coord)
        if((max_pressure > threshold_heal) and (distance_max_y_to_last_y < distance_max_y_to_first_y)): # Special case for the begining of the test and turn 1
            event = Tug_Event.heel
            if(x_max_pressure > 14):
                placement = Placement.right
            else:
                placement = Placement.left
        else:
            event = Tug_Event.foot
            if(right_side_total_pressure > left_side_total_pressure):
                placement = Placement.left
            else:
                placement = Placement.right    
        write_to_csv(filepath_TED, metrics['timestamp'], event, placement, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk2

def on_turn_1(metrics, filepath_TED):
    y_distance = metrics['y_distance']

    # First turn during TUG (turning at the end of the walkway to walk back to the chair)
    if(y_distance > 20):
        # Indicates that we started walking again after turning
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.walk2, None, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk2
    else:
        # Still turning 
        return Tug_State.turn1

def on_turn_2(metrics, filepath_TED):
    pressure_on_seat = metrics['seat_total_pressure']

    # Second turn during TUG (turning to sit back down)
    if(pressure_on_seat > threshold_seat):
        # Indicates that we are done turning and now sitting
        write_to_csv(filepath_TED, metrics['timestamp'],Tug_Event.sit, None, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.sit
    else:
        # Still turning 
        return Tug_State.turn2

def on_sit(metrics, filepath_TED):
    write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.end, None, None, None, None)
    return 0,0

def calculate_metrics(floor_frame, seat_frame):
    metrics = {}
    
    # Calculate and store metrics in dictionary
    metrics['cop_x'], metrics['cop_y'] = calc_cop(floor_frame)
    metrics['total_pressure'] = calc_total_pressure(floor_frame)
    metrics['seat_total_pressure'] = calc_total_pressure(seat_frame)
    metrics['max_pressure'], metrics['x_coord_max_pressure'], metrics['y_coord_max_pressure'] = calc_max_pressure(floor_frame)
    metrics['y_distance'], metrics['y_first_coord'], metrics['y_last_coord'] = calc_y_distance(floor_frame)
    metrics['left_side_total_pressure'], metrics['right_side_total_pressure'] = calc_separate_side_total_pressure(floor_frame)

    return metrics

def run_analysis(file_path_mat1, file_path_mat2, file_path_seat, filepath_TED):
    index = 0
    current_state = Tug_State.prep
    next_state = Tug_State.prep

    timestamp_list, floor_array, seat_array = load_files(file_path_mat1, file_path_mat2, file_path_seat)

    while index < len(timestamp_list):
        floor_frame = floor_array[index, :, :]
        seat_frame = seat_array[index, :, :] 

        # Create dictionary with metrics
        metrics = calculate_metrics(floor_frame, seat_frame)
        metrics['timestamp'] = timestamp_list.loc[index, 'timestamp'] 
        next_state= get_next_state(current_state, metrics, filepath_TED)
        
        current_state = next_state
        index += 1

    return True

def get_next_state(current_state, metrics, filepath_TED):

    match current_state:

        case Tug_State.prep:
            return on_prep(metrics, filepath_TED)

        case Tug_State.stand:
            return on_stand(metrics, filepath_TED)

        case Tug_State.walk1:
            return on_walk_1(metrics, filepath_TED)

        case Tug_State.turn1:
            return on_turn_1(metrics, filepath_TED)

        case Tug_State.walk2:
            return on_walk_2(metrics, filepath_TED)

        case Tug_State.turn2:
            return on_turn_2(metrics, filepath_TED)   
            
        case Tug_State.sit:
            return on_sit(metrics, filepath_TED)

def get_file_paths(test):

    if test == 'test 1':
        file_path_mat1 = 'MALISA_Python/data/tug1_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug1_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug1_seat.csv'
    if test == 'test 2':
        file_path_mat1 = 'MALISA_Python/data/tug2_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug2_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug2_seat.csv'
    if test == 'test 3':
        file_path_mat1 = 'MALISA_Python/data/tug3_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug3_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug3_seat.csv'
    if test == 'test 4':
        file_path_mat1 = 'MALISA_Python/data/tug4_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug4_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug4_seat.csv'  

    return file_path_mat1, file_path_mat2, file_path_seat 

def create_heatmaps_and_plot(floor_frame, seat_frame):
    # Create subplots for both floor mats and seat mat
    fig = make_subplots(rows=2, cols=1, row_heights=[150, 1200])

    # 12 bits gives a resolution of 4096 values, including 0 -> 4095
    fig.add_trace(go.Heatmap(z=seat_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=floor_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=2, col=1)

    # Update layout
    fig.layout.height = 1350
    fig.layout.width = 210
    fig.update(layout_showlegend=False)

    # Show the plotly chart
    st.plotly_chart(fig)

def plot_floor(floor_frame):
    fig = go.Figure(data=go.Heatmap(z=floor_frame, zmin=0, zmax=4095, colorscale='Plasma'))
    fig.update_layout(height=1600, width=280)  # Update layout properties
    st.plotly_chart(fig)

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
    test = st.selectbox(label='Select TUG test', options=['test 1', 'test 2', 'test 3', 'test 4'])

    file_path_mat1, file_path_mat2, file_path_seat = get_file_paths(test)

    # Load data for sensor floor mats
    timestamp_list, floor_array, seat_array = load_files(file_path_mat1, file_path_mat2, file_path_seat)

    # Create CSV file for test to save tug event data (TED) 
    filepath_TED = create_filepath('DS', test)
    create_csv_file(filepath_TED)

    mode = st.selectbox(label='Select Mode', options=['Run Analysis', 'Visual Analysis'])

    if mode == 'Run Analysis':
        if st.button("RUN"):
            run_analysis(file_path_mat1, file_path_mat2, file_path_seat, filepath_TED)

    if mode == 'Visual Analysis':
        col1, col2 = st.columns([3, 2])  # Ratio of column widths
        with col1:
            index = st.slider('Choose frame', 0, len(timestamp_list)-1, key='frame_slider')

            floor_frame = floor_array[index, :, :]
            seat_frame = seat_array[index, :, :] 

            # Create dictionary with metrics
            metrics = calculate_metrics(floor_frame, seat_frame)
            metrics['timestamp'] = timestamp_list.loc[index, 'timestamp']

            create_table(metrics)
        with col2:
            #create_heatmaps_and_plot(floor_frame, seat_frame)
            plot_floor(floor_frame)

main()