import pandas as pd
from pressure_sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

# Thresholds
threshold_seat = 3600
threshold_heal = 4000
threshold_y = 60
y_dis_low = 5
y_dis_high = 20


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

def on_prep(metrics, filepath_TED):
    seat_total_pressure = metrics['seat_total_pressure']
    
    if(seat_total_pressure < threshold_seat):
        # If total pressure on seat is below threshold T_sit_to_stand then log event stand
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.start, None, None, None)
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.stand, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.stand
    else:
        return Tug_State.prep
    
def on_stand(metrics, filepath_TED):
    cop_y = metrics['cop_y']

    if(cop_y < threshold_y):
        # If current total pressure is reaching max pressure threshold, 
        # then logg walk because it indicates first valid heel after standing position
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.walk1, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk1
    else:
        # Else logg that we are still in stand state
        return Tug_State.stand

def on_walk_1(metrics, filepath_TED):
    cop_y = metrics['cop_y']

    # The first walk during TUG (walking away from the chair)
    if (cop_y > threshold_y):
        # Indicates that we are now turning around to start walking back
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.turn1, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.turn1
    else:
        # Still walking, estimate and log heel or foot
        estimate_gait(metrics, 1, filepath_TED)
        return Tug_State.walk1

def on_walk_2(metrics, filepath_TED):
    cop_y = metrics['cop_y']
    event = {}

     # On second walk (walk back)
    if(cop_y > threshold_y):
        # Indicates that we are now turning around to evantually sit down
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.turn2, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.turn2
    else:
        # Still walking, estimate and log heel or foot
        estimate_gait(metrics, 2, filepath_TED)
        return Tug_State.walk2

def on_turn_1(metrics, filepath_TED):
    cop_y = metrics['cop_y']

    # First turn during TUG (turning at the end of the walkway to walk back to the chair)
    if(cop_y < threshold_y):
        # Indicates that we started walking again after turning
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.walk2, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.walk2
    else:
        # Still turning 
        return Tug_State.turn1

def on_turn_2(metrics, filepath_TED):
    pressure_on_seat = metrics['seat_total_pressure']

    # Second turn during TUG (turning to sit back down)
    if(pressure_on_seat > threshold_seat):
        # Indicates that we are done turning and now sitting
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.sit, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])
        return Tug_State.sit
    else:
        # Still turning 
        return Tug_State.turn2

def on_sit(metrics, filepath_TED):
    # log 
    write_to_csv(filepath_TED, metrics['timestamp'], Tug_Event.end, None, None, None)
    return 0,0

def estimate_gait(metrics, walk_nr, filepath_TED):
    x_cord_max_pressure = metrics['x_cord_max_pressure']
    current_max_pressure = metrics['max_pressure']
    y_dis = metrics['y_distance']
    mat_nr = metrics['mat_nr']
    event = None
    placement = estimate_placement(walk_nr, mat_nr, x_cord_max_pressure) # right or left

    if(current_max_pressure > threshold_heal and (y_dis > y_dis_high or y_dis < y_dis_low)):
        if (placement == Placement.left):
            event = Tug_Event.left_heel
        else:
            event = Tug_Event.right_heel
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], event, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])

    elif (1600 < current_max_pressure < 2900 and y_dis <= 12):
        if (placement == Placement.left):
            event = Tug_Event.left_foot
        else:
            event = Tug_Event.right_foot
        # LOG
        write_to_csv(filepath_TED, metrics['timestamp'], event, metrics['cop_x'], metrics['cop_y'], metrics['total_pressure'])


def estimate_placement(walk_nr, mat, x):
# x is the coordinate holding max pressure
    if (walk_nr == 1 and mat == 1):
        if x >= 14:
            return Placement.left
        elif x < 14:
            return Placement.right
                
    elif (walk_nr == 1 and mat == 2):
        if x >= 14:
            return Placement.right
        elif x < 14:
            return Placement.left
        
    elif (walk_nr == 2 and mat == 2):
        if x < 14:
            return Placement.right
        elif x >= 14:
            return Placement.left
                
    elif (walk_nr == 2 and mat == 1):
        if x < 14:
            return Placement.left
        elif x >= 14:
            return Placement.right
    
    return None

def calculate_metrics(floor_frames, seat_frame):
    metrics = {}
    
    # Calculate and store metrics in dictionary
    metrics['cop_x'], metrics['cop_y'], metrics['mat_nr'] = calc_cop(floor_frames)
    metrics['total_pressure'] = calc_total_pressure(floor_frames)
    metrics['seat_total_pressure'] = calc_total_pressure(seat_frame)
    metrics['max_pressure'], metrics['x_cord_max_pressure'] = find_max_pressure(floor_frames)
    metrics['pressure_area'] = calc_area(floor_frames)
    metrics['y_distance'] = calc_y_distance(floor_frames)
    
    return metrics

def create_event_table(timestamp, event, cop_x, cop_y):
    event_table = {}

    event_table['timestamp'] = timestamp
    event_table['event'] = event
    event_table['cop_x'] = cop_x
    event_table['cop_y'] = cop_y

    return event_table

def run_analysis(file_path_mat1, file_path_mat2, file_path_seat, filepath_TED):
    index = 0
    current_state = Tug_State.prep
    next_state = Tug_State.prep

    timestamp_list, floor1_array, floor2_array, seat_array = load_files(file_path_mat1, file_path_mat2, file_path_seat)

    while index < len(timestamp_list):
        floor1_frame = floor1_array[index, :, :]
        floor2_frame = floor2_array[index, :, :]
        seat_frame = seat_array[index, :, :] 

        # Create dictionary with metrics
        metrics = calculate_metrics([floor1_frame, floor2_frame], seat_frame)
        metrics['timestamp'] = timestamp_list.loc[index, 'timestamp'] 
        next_state= get_next_state(current_state, metrics, filepath_TED)
        
        # Here -> save event_table in csv file
        
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

    if test == '1':
        file_path_mat1 = 'MALISA_Python/data/tug1_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug1_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug1_seat.csv'
    if test == '2':
        file_path_mat1 = 'MALISA_Python/data/tug2_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug2_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug2_seat.csv'
    if test == '3':
        file_path_mat1 = 'MALISA_Python/data/tug3_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug3_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug3_seat.csv'
    if test == '4':
        file_path_mat1 = 'MALISA_Python/data/tug4_mat1.csv'
        file_path_mat2 = 'MALISA_Python/data/tug4_mat2.csv'
        file_path_seat = 'MALISA_Python/data/tug4_seat.csv'  

    return file_path_mat1, file_path_mat2, file_path_seat   

def create_heatmaps_and_plot(floor1_frame, floor2_frame, seat_frame):
    # Create subplots for both floor mats and seat mat
    fig = make_subplots(rows=1, cols=3, column_widths=[280, 280, 200], row_heights=[800])

    # 12 bits gives a resolution of 4096 values, including 0 -> 4095
    fig.add_trace(go.Heatmap(z=floor1_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=floor2_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=2)
    fig.add_trace(go.Heatmap(z=seat_frame, zmin=0, zmax=4095, colorscale='Plasma'), row=1, col=3)

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

def create_table(metrics):
    info = [('timestamp', metrics['timestamp'][:21]), ('cop X', metrics['cop_x']), ('cop Y', metrics['cop_y']), ('mat nr', metrics['mat_nr']), ('seat total pressure', metrics['seat_total_pressure']), ('floor total pressure', metrics['total_pressure']), ('Y distance', metrics['y_distance']), ('X-cord (max pres.)', metrics['x_cord_max_pressure'])]
    info = pd.DataFrame(info, columns=['Metric', 'Value'])
    st.table(info)


def main():

    print("Choose test: (1, 2, 3, or 4):")

    test = input()

    file_path_mat1, file_path_mat2, file_path_seat = get_file_paths(test)

    # create CSV file for test to save tug event data (TED)  
    filepath_TED = create_filepath('DS', test)

    create_csv_file(filepath_TED)

    run_analysis(file_path_mat1, file_path_mat2, file_path_seat, filepath_TED)


main()