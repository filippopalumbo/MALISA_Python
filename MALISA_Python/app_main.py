from state_machine import *
from csv_handler import *
from parameter_calculations import *
from visualiser import *
from preprocessing import *
import streamlit as st

def filter_files(file_list, keyword):
    #Filter the files on keyword
    filtered_files = [file for file in file_list if keyword in file]
    #Sort the files alphabetically
    filtered_files.sort() 
    return filtered_files

def file_selector_sensor_data_floor_1(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    floor_1_files = filter_files(filenames, "floor1")
    selected_filename = st.selectbox('File Fitness Mat 1', floor_1_files)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_floor_2(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    floor_2_files = filter_files(filenames, "floor2")
    selected_filename = st.selectbox('File Fitness Mat 2', floor_2_files)
    return os.path.join(folder_path, selected_filename)

def file_selector_sensor_data_seat(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    seat_files = filter_files(filenames, "seat")
    selected_filename = st.selectbox('File Seat Mat', seat_files)
    return os.path.join(folder_path, selected_filename)

def file_selector_tug_analysis(folder_path='./MALISA_Python/analyzed_data'):
    filenames = os.listdir(folder_path)
    #Sort the files alphabetically
    filenames.sort() 
    selected_filename = st.selectbox('Select file', filenames)
    return os.path.join(folder_path, selected_filename)

def main():
    st.title('TUG Analysis Web Application')

    # Sidebar menu
    with st.sidebar:
        st.subheader('Choose Mode')
        mode = st.selectbox(label='', options=['Run Analysis', 'View Results'])
    
    # Main area
    if mode == 'Run Analysis':
        st.markdown('1. Select the files of the the test you want to run analysis on.')
        st.markdown('2. Press "RUN".')

        file_floor_1 = file_selector_sensor_data_floor_1()
        file_floor_2 = file_selector_sensor_data_floor_2()
        file_seat = file_selector_sensor_data_seat()
        
        filename = os.path.basename(file_floor_1) 
        initials, test_id, _ = filename.split('_')

        if st.button('RUN'):
            # Save files with identical names in the processed data folder
            process(file_floor_1, file_floor_2, file_seat, initials, test_id)

            tug_analysis_filepath = create_filepath(initials, test_id)
            create_csv_file(tug_analysis_filepath)

            run_analysis(f'MALISA_Python/processed_data/{initials}_{test_id}_floor1.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_floor2.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_seat.csv', tug_analysis_filepath)

    else:
        st.markdown('1. Select the file of the the test you want view the results of.')
        st.markdown('2. Choose wether to view results and/or play the test back.')
        
        filepath = file_selector_tug_analysis()
        
        filename = os.path.basename(filepath) 
        
        initials, test_id, _ = filename.split('_')

        results = st.checkbox('Results')
        visuals = st.checkbox('Visual Playback')

        if results:
            parameters = calculate_parameters(filepath)

            table = create_table(parameters)
            st.dataframe(table)

        if visuals:
            # Load data for sensor floor mats
            timestamp_list, floor1_array, floor2_array, seat_array = load_files(f'MALISA_Python/processed_data/{initials}_{test_id}_floor1.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_floor2.csv', f'MALISA_Python/processed_data/{initials}_{test_id}_seat.csv')

            index = st.slider('Choose frame', 0, len(timestamp_list)-1)

            floor1_frame = floor1_array[index, :, :]
            floor2_frame = floor2_array[index, :, :]
            seat_frame = seat_array[index, :, :] 

            fig = create_heatmaps(floor1_frame, floor2_frame, seat_frame)
            
            st.plotly_chart(fig)

main()