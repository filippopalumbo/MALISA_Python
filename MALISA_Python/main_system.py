from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import time

def collect_sensor_data(pathname, port_mat_1): #, port_mat_2, port_seating_mat):
    i = 0
    while st.session_state.stop_flag == False:
        print("i: " + str(i))
        time.sleep(2)
        i+=1
    # start consoles here 

def click_start_button():
    st.session_state.start_clicked = True
    st.session_state.stop_clicked = False
    st.session_state.stop_flag = False
    st.session_state.start_disabled = True
    st.session_state.stop_disabled = False

def click_stop_button():
    st.session_state.stop_clicked = True
    st.session_state.start_clicked = False
    st.session_state.start_disabled = False
    st.session_state.stop_disabled = True
    
def main():
    # Initialization
    if 'start_clicked' not in st.session_state:
        st.session_state.start_clicked = False
    if 'start_disabled' not in st.session_state:
        st.session_state.start_disabled = False
    if 'stop_clicked' not in st.session_state:
        st.session_state.stop_clicked = False
    if 'stop_disabled' not in st.session_state:
        st.session_state.stop_disabled = True
   
    if 'stop_flag' not in st.session_state:
        st.session_state.stop_flag = False # Flag to stop the while-loop collecting sensor data
    if "ideal" not in st.session_state:
        st.session_state.ideal = False
    if "default" not in st.session_state:
        st.session_state.default = False


    st.button('START', on_click=click_start_button, disabled=st.session_state.start_disabled)
    st.button('STOP', on_click=click_stop_button, disabled=st.session_state.stop_disabled)

    # if st.session_state.ideal:
     # Add code in Streamlit for the user to add information about pathname 
    pathname = st.text_input("Enter Pathname", "")
    st.write('You entered:', pathname)

    # Add code in Streamlit for the user to add information about comport
    port_mat_1 = st.text_input("Enter port", "")
    st.write('You entered:', port_mat_1)
    # port_mat_2 = st.text_input("Enter port", "")
    # st.write('You entered:', port_mat_1)
    # port_seating_mat = st.text_input("Enter port", "")
    # st.write('You entered:', port_mat_1)


    if st.session_state.start_clicked:
        # Check if port is a number
        if port_mat_1.isdigit() and pathname != "" and port_mat_1 != "":
            # The message and nested widget will remain on the page
            st.write('Start button clicked!')
            st.session_state.start_disabled = True
            st.session_state.stop_disabled = False
            st.session_state.default = False
            st.session_state.start_clicked = False

            collect_sensor_data(pathname, port_mat_1)
        else:
            st.session_state.default = True
            st.session_state.start_disabled = False
            st.session_state.stop_disabled = True


    if st.session_state.stop_clicked:
        # The message and nested widget will remain on the page
        st.write('Stop button clicked!')
        st.session_state.stop_flag = True
        st.session_state.stop_clicked = False
    

    if st.session_state.default:
        st.write('Enter pathname and port again!')
        st.session_state.default = False

        
        

main()


