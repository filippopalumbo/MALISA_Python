from state_machine import *
from csv_handler import *
from parameter_calculations import *
from preprocessing import *
import streamlit as st

def file_selector_sensor_data_floor_1(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select file with sensor data of Fitness Mat 1', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_floor_2(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select file with sensor data of Fitness Mat 2', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_seat(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select file with sensor data of Seat Mat', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_tug_analysis(folder_path='./MALISA_Python/analyzed_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select analyzed file', filenames)
    return os.path.join(folder_path, selected_filename)

def create_table(parameters):
    tug_time_seconds = parameters['tug_time'].seconds + parameters['tug_time'].microseconds/1000000
    stand_up_time_seconds = parameters['stand_up_time'].seconds + parameters['stand_up_time'].microseconds/1000000
    turn_between_walks_time_seconds = parameters['turn_between_walks_time'].seconds + parameters['turn_between_walks_time'].microseconds/1000000
    turn_before_sit_time_seconds = parameters['turn_before_sit_time'].seconds + parameters['turn_before_sit_time'].microseconds/1000000

    info = [('TUG time', 's', tug_time_seconds),
            ('Stand up time', 's', stand_up_time_seconds),
            ('Turn between walks time', 's', turn_between_walks_time_seconds),
            ('Turn before sit time', 's', turn_before_sit_time_seconds),
            ('Walk speed', 'm/s', parameters['walk_speed']),
            ('Stride Length', 'cm', parameters['stride_length'])]

    info = pd.DataFrame(info, columns=['Parameter', 'Unit' ,'Value'])
    st.table(info)

def main():
    st.title('TUG Analysis Web Application')
    # Sidebar menu
    with st.sidebar:
        st.subheader('Choose Mode')
        mode = st.selectbox(label='', options=['Run Analysis', 'View Results'])
    
    # Main area
    if mode == 'Run Analysis':
        st.subheader('Run analysis on raw sensor data')
        file_floor_1 = file_selector_sensor_data_floor_1()
        file_floor_2 = file_selector_sensor_data_floor_2()
        file_seat = file_selector_sensor_data_seat()

        initials = st.text_input('Initials of subject', '')
        test_id = st.text_input('Id of test', '')

        if st.button('RUN'):
            # Save files with identical names in the processed data folder
            #process(file_floor_1, file_floor_2, file_seat)
            tug_analysis_filepath = create_filepath(initials, test_id)
            create_csv_file(tug_analysis_filepath)

            # When testing on raw data, update the filepath to the processed file
            #run_analysis(f'MALISA_Python/processed_data/{file_floor_1.name}', f'MALISA_Python/processed_data/{file_floor_2.name}', f'MALISA_Python/processed_data/{file_seat.name}', tug_analysis_filepath)

            # When testing on already processed data, no need to update the filepath
            run_analysis(file_floor_1, file_floor_2, file_seat, tug_analysis_filepath)
    else:
        st.subheader('View the results of a stored TUG-test')
        filename = file_selector_tug_analysis()
        if st.button('VIEW'):
            parameters = calculate_parameters(filename)
            create_table(parameters)

main()