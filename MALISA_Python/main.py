from state_machine import *
from csv_handler import *
from parameter_calculations import *
import streamlit as st

def click_run_button():
    # Only happens once - when the button is clicked
    st.session_state.run_clicked = True
    st.session_state.file_floor_1_disabled = True
    st.session_state.file_floor_2_disabled = True
    st.session_state.file_seat_disabled = True
    st.session_state.run_disabled = False

def enable_run():
    st.session_state.run_disabled = False

def disable_run():
    st.session_state.run_disabled = True

def file_selector_raw_sensor_data(folder_path='./MALISA_Python/sensor_data'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select the generated analysis file', filenames)
    return os.path.join(folder_path, selected_filename)

def file_selector_tug_analysis(folder_path='./MALISA_Python/tug_analysis_files'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select the generated analysis file', filenames)
    return os.path.join(folder_path, selected_filename)

def calculate_parameters(filepath):
    events_df = pd.read_csv(filepath)
    events_csv = read_csv_data(filepath)
    parameters = {}
    parameters['tug_time'] = calc_tug_time(events_df)
    parameters['stand_up_time'] = calc_stand_up_time(events_df)
    parameters['turn_between_walks_time'] = calc_turn_between_walks_time(events_df)
    parameters['turn_before_sit_time'] = calc_turn_before_sit_time(events_df)
    parameters['walk_speed'] = calc_walk_speed(events_df)
    parameters['stride_length'] = calc_stride_length(events_csv)

    return parameters

def create_table(parameters):
    info = [('TUG time', 's', parameters['tug_time']),
            ('Stand up time', 's', parameters['stand_up_time']),
            ('Turn between walks time', 's', parameters['turn_between_walks_time']),
            ('Turn before sit time', 's', parameters['turn_before_sit_time']),
            ('Walk speed', 'm/s', parameters['walk_speed'])
            ('Stride Length', 'm', parameters['stride_length'])]

    info = pd.DataFrame(info, columns=['Parameter', 'Unit' ,'Value'])
    st.table(info)

def main():

    # Sidebar menu
    with st.sidebar:
        st.subheader('Main Menu')
        mode = st.selectbox(label='Select Mode', options=['Run Analysis', 'View Results'])
    
    # Main area
    if mode == 'Run Analysis':
        st.subheader('Lets analyse!')
        file_floor_1 = st.file_uploader("Upload floor 1 csv-file", accept_multiple_files=False)
        file_floor_2 = st.file_uploader("Upload floor 2 csv-file", accept_multiple_files=False)
        file_seat = st.file_uploader("Upload seat csv-file", accept_multiple_files=False)
        initials = st.text_input('Initials of subject', '')
        test_id = st.text_input('Id of test', '')

        if st.button('RUN'):
            tug_analysis_filepath = create_filepath(initials, test_id)
            create_csv_file(tug_analysis_filepath)
            run_analysis(file_floor_1, file_floor_2, file_seat, tug_analysis_filepath)
    else:
        st.subheader('Lets view results')
        filename = file_selector_tug_analysis()
        if st.button('VIEW'):
            parameters = calculate_parameters(filename)
            create_table(parameters)

main()