import pandas as pd
from calculations import *
from enumnum.tug_events import *
from enumnum.tug_states import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

T_sit_to_stand = 3600
T_max_pressure = 4000

def load_seat_file(file_path): 
    df = []
    df = pd.read_csv(file_path) 
    
    return df

def load_floor_files(file_paths):
    dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dfs.append(df)

    return dfs

def on_prep(frame):
    tot_pressure = calc_total_pressure(frame)

    if(tot_pressure < T_sit_to_stand):
        return Tug_State.stand,0
    else:
        return Tug_State.prep,0
    

def on_stand(metrics):
    current_tot_pressure = metrics['max_pressure']

    if(current_tot_pressure > T_max_pressure):
        return Tug_State.walk1,0
    else:
        return Tug_State.stand,0
    

def on_walk(metrics, walk_nr):
    return 0,0

def on_turn(metrics, turn_nr):
    return 0,0

def on_sit(metrics):
    return 0,0

def estimate_placement(walk, mat, cop_x):

    if (walk == Tug_Event.walk1 and mat == 1):
        if cop_x >= 14:
            return Placement.left
        elif cop_x < 14:
            return Placement.right
                
    elif (walk == Tug_Event.walk1 and mat == 2):
        if cop_x >= 14:
            return Placement.right
        elif cop_x < 14:
            return Placement.left
        
    elif (walk == Tug_Event.walk2 and mat == 2):
        if cop_x < 14:
            return Placement.right
        elif cop_x >= 14:
            return Placement.left
                
    elif (walk == Tug_Event.walk2 and mat == 1):
        if cop_x < 14:
            return Placement.left
        elif cop_x >= 14:
            return Placement.right
    
    return None

def calculate_metrics(frames):
    metrics = {}
    
    # Calculate metrics
    cop_x, cop_y, mat_nr = calc_cop(frames)
    total_pressure = calc_total_pressure(frames)
    max_pressure = find_max_pressure(frames)
    pressure_area = calc_area(frames)
    
    # Store metrics in the dictionary
    metrics['cop_x'] = cop_x
    metrics['cop_y'] = cop_y
    metrics['mat_nr'] = mat_nr
    metrics['total_pressure'] = total_pressure
    metrics['max_pressure'] = max_pressure
    metrics['pressure_area'] = pressure_area
    
    return metrics

def create_event_table(timestamp, event, cop_x, cop_y):
    event_table = {}

    event_table['timestamp'] = timestamp
    event_table['event'] = event
    event_table['cop_x'] = cop_x
    event_table['cop_y'] = cop_y

    return event_table

def run_analysis(mat1, mat2, seat):
    index = 0
    current_state = Tug_State.prep

    # When reshaping the dataframes mat1 and mat2 for calculations the timestamps are removed
    # We keep mat1 and mat2 as dataframes-types to retrieve the timestamps
    mat1_array = mat1.iloc[:, 1:].to_numpy().reshape(len(mat1), 80, 28)
    mat2_array = mat2.iloc[:, 1:].to_numpy().reshape(len(mat2), 80, 28)
    seat_array = seat.iloc[:, 1:].to_numpy().reshape(len(seat), 20, 20)

    # Clear data of values below threshold 
    mat1_array[mat1_array < 400] = 0
    mat2_array[mat2_array < 400] = 0
    seat_array[seat_array < 100] = 0

    while index < len(mat1):
        floor1_frame = mat1_array[index, :, :]
        floor2_frame = mat2_array[index, :, :]
        seat_frame = seat_array[index, :, :] 

        # Create dictionary with metrics
        metrics = calculate_metrics([floor1_frame, floor2_frame])
        next_state, event_table = get_next_state(current_state, metrics, seat_frame)

        # Here log information in event_table !!
        
        current_state = next_state
        index += 1

    return True

def get_next_state(current_state, metrics, seat_frame):
    
    match current_state:

        case Tug_State.prep:
            next_state, event_table = on_prep(seat_frame)

        case Tug_State.stand:
            next_state, event_table = on_stand(metrics)

        case Tug_State.walk1:
            next_state, event_table = on_walk(metrics, 1)

        case Tug_State.turn1:
            next_state, event_table = on_turn(metrics, 1)

        case Tug_State.walk2:
            next_state, event_table = on_walk(metrics, 2)

        case Tug_State.turn2:
            next_state, event_table = on_turn(metrics, 2)   
            
        case Tug_State.sit:
            next_state, event_table = on_sit(metrics)

    return next_state, event_table

def create_heatmap(frame):
    # 12 bits gives a resolution of 4096 values, including 0 -> 4095
    heatmap_trace = go.Heatmap(z=frame, zmin=0, zmax=4095, colorscale='Plasma') 
    return heatmap_trace

def main():
    test = st.selectbox(label='Select TUG test', options=['test 1', 'test 2', 'test 3', 'test 4'])

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
    
    # Load data for sensor floor mats
    mat1, mat2 = load_floor_files([file_path_mat1, file_path_mat2])

    # Load data for sensor seat mat
    seat = load_seat_file(file_path_seat)

    mode = st.selectbox(label='Select MODE', options=['Run Analysis', 'Validate'])

    if mode == 'Run Analysis':
        if st.button('RUN'):
            run_analysis(mat1, mat2, seat)

    if mode == 'Validate':
        index = st.slider('Choose frame', 0, len(mat1)-1)

        # When reshaping the dataframes mat1 and mat2 for calculations the timestamps are removed
        # That is why we need to keep mat1 and mat2 as dataframes-types to retrieve the timestamps
        mat1_array = mat1.iloc[:, 1:].to_numpy().reshape(len(mat1), 80, 28)
        mat2_array = mat2.iloc[:, 1:].to_numpy().reshape(len(mat2), 80, 28)
        seat_array = seat.iloc[:, 1:].to_numpy().reshape(len(seat), 20, 20)

        # Clear data of values below threshold
        mat1_array[mat1_array < 400] = 0
        mat2_array[mat2_array < 400] = 0
        seat_array[seat_array < 100] = 0

        current_state = Tug_State.prep

        floor1_frame = mat1_array[index, :, :]
        floor2_frame = mat2_array[index, :, :]
        seat_frame = seat_array[index, :, :] 

        # Create dictionary with metrics
        metrics = calculate_metrics([floor1_frame, floor2_frame])
        next_state, event_table = get_next_state(current_state, metrics, seat_frame)

        info = [('timestamp', mat1.loc[index, 'timestamp']),('event', current_state),('cop X', metrics['cop_x']),('cop Y', metrics['cop_y'])]
        info = pd.DataFrame(info, columns=['Column', 'Value'])
        st.table(info)

        current_state = next_state

        # Create subplots for both floor mats and seat mat
        fig = make_subplots(rows=1, cols=3, column_widths=[280, 280, 200], row_heights=[800])

        fig.add_trace(create_heatmap(floor1_frame), row=1, col=1)
        fig.add_trace(create_heatmap(floor2_frame), row=1, col=2)
        fig.add_trace(create_heatmap(seat_frame), row=1, col=3)

        # Update layout
        fig.layout.height = 800
        fig.layout.width = (280 * 2) + 200
        # Adjust the heights of specific rows
        fig.update_layout(
            yaxis1=dict(domain=[0, 800/1000]),  # Adjust the height of the first row
            yaxis2=dict(domain=[0, 800/1000]),  # Adjust the height of the second row
            yaxis3=dict(domain=[0, 200/1000])   # Adjust the height of the third row
        )
        fig.update_layout(showlegend=False)

        # Show the plotly chart
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()