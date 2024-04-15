from state_machine import *
from csv_handler import *
from parameter_calculations import *
from preprocessing import *
import streamlit as st
import plotly.graph_objects as go  
from plotly.subplots import make_subplots

def file_selector_sensor_data_floor_1(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Fitness Mat 1', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_floor_2(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Fitness Mat 2', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_seat(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('File Seat Mat', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_tug_analysis(folder_path='./MALISA_Python/analyzed_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select file', filenames)
    return os.path.join(folder_path, selected_filename)

def create_table(parameters):
    tug_time_seconds = parameters['tug_time'].seconds + parameters['tug_time'].microseconds/1000000
    stand_up_time_seconds = parameters['stand_up_time'].seconds + parameters['stand_up_time'].microseconds/1000000
    turn_between_walks_time_seconds = parameters['turn_between_walks_time'].seconds + parameters['turn_between_walks_time'].microseconds/1000000
    turn_before_sit_time_seconds = parameters['turn_before_sit_time'].seconds + parameters['turn_before_sit_time'].microseconds/1000000

    info = [('TUG time', tug_time_seconds, 's'),
            ('Sit to Stand', stand_up_time_seconds, 's'),
            ('Mid Turning', turn_between_walks_time_seconds, 's'),
            ('End Turning Stand to Sit', turn_before_sit_time_seconds, 's'),
            ('Walk speed', parameters['walk_speed'], 'm/s'),
            ('Stride Length', parameters['stride_length'], 'cm')]

    info = pd.DataFrame(info, columns=['Parameter', 'Value' , 'Unit'])
    info['Value'] = info['Value'].round(2)
    st.dataframe(info)

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

def create_heatmaps_and_plot(floor1_frame, floor2_frame, seat_frame):
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

    # Show the plotly chart
    st.plotly_chart(fig)

def main():
    st.title('TUG Analysis Web Application')

    # Sidebar menu
    with st.sidebar:
        st.subheader('Choose Mode')
        mode = st.selectbox(label='', options=['Run Analysis', 'View Results'])
    
    # Main area
    if mode == 'Run Analysis':
        st.markdown('1. Select the files of the the test you want to run analysis on.')
        st.markdown('2. Enter the initials of the subject and the id of the test.')
        st.markdown('3. Press "RUN".')

        file_floor_1 = file_selector_sensor_data_floor_1()
        file_floor_2 = file_selector_sensor_data_floor_2()
        file_seat = file_selector_sensor_data_seat()

        initials = st.text_input('Initials', '')
        test_id = st.text_input('Id', '')

        if st.button('RUN'):
            # Save files with identical names in the processed data folder
            process(file_floor_1, file_floor_2, file_seat, initials, test_id)

            tug_analysis_filepath = create_filepath(initials, test_id)
            create_csv_file(tug_analysis_filepath)

            # When testing on raw data, update the filepath to the processed file
            run_analysis(f'MALISA_Python/processed_data/{initials}_{test_id}_floor1.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_floor2.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_seat.csv', tug_analysis_filepath)

    else:
        st.markdown('1. Select the file of the the test you want view the results of.')
        st.markdown('2. Enter the initials of the patient and the id of the test.')
        st.markdown('3. Choose wether to view results and/or see the recording.')
        filename = file_selector_tug_analysis()
        initials = st.text_input('Initials', '')
        test_id = st.text_input('Id', '')
        results = st.checkbox('Results')
        visuals = st.checkbox('Visual Playback')

        if results:
            parameters = calculate_parameters(filename)
            create_table(parameters)

        if visuals:
            # Load data for sensor floor mats
            timestamp_list, floor1_array, floor2_array, seat_array = load_files(f'MALISA_Python/processed_data/{initials}_{test_id}_floor1.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_floor2.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_seat.csv')

            index = st.slider('Choose frame', 0, len(timestamp_list)-1)

            floor1_frame = floor1_array[index, :, :]
            floor2_frame = floor2_array[index, :, :]
            seat_frame = seat_array[index, :, :] 

            create_heatmaps_and_plot(floor1_frame, floor2_frame, seat_frame)

main()