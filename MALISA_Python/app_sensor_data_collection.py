"""
Summary:
This Streamlit application is designed to simultaneously collect raw sensor data from three different 
serial ports. It interfaces with various sensor devices, including seating mats and fitness mats, 
to gather data. The collected data is then stored in CSV files for further analysis.

Purpose:
The purpose of this application is to facilitate the collection of sensor data from multiple devices 
simultaneously. It enables researchers or users to conduct experiments or gather data from various 
sensors efficiently. The collected data can be used for analysis, research, or monitoring purposes in 
fields such as healthcare, sports science, or human-computer interaction.

Usage:
1. Open the Streamlit application.
2. Enter the appropriate serial port for each sensor device.
3. Click the "Submit" button to confirm port configurations.
4. Press the "Start" button to initiate data collection.
5. Perform the desired activity or experiment while data is being collected.
6. Once the data collection is complete, press the "Stop" button to end the test.
7. Enter initials and test number to identify the collected data.
8. Click the "Submit" button to save the collected data with appropriate identifiers.
9. Repeat the process for additional tests or experiments.
10. Restart the application if needed to configure new ports or start a new session. (Feature currently in development)

Author: [Malin Ramkull & Hedda Eriksson]
Date: [10 april 2024]
"""
import streamlit as st
import time
import threading
import numpy as np
import serial
import base64
import csv_handler
import sensor_SW.seating_mat as seating_mat
import sensor_SW.fitness_mat as fitness_mat

PORT_SEAT = ''    # '/dev/tty.usbserial-1120'
PORT_FLOOR1 = ''   #'/dev/tty.usbmodem84214601' 
PORT_FLOOR2 =  ''
ROWS_SEAT = 20  
COLS_SEAT = 20  
ROWS_FLOOR = 80  
COLS_FLOOR = 28
FILEPATH_SEAT = "MALISA_Python/sensor_data/thread_seat.csv"
FILEPATH_FLOOR1 = "MALISA_Python/sensor_data/thread_floor1.csv"
FILEPATH_FLOOR2 = "MALISA_Python/sensor_data/thread_floor2.csv"

debug = False

def data_collector_floor1(port, event):
    # Connects to serial port
    ser = serial.Serial(
        port,
        baudrate=115200,
        timeout=0.1
    )

    # Skip BLE advertising string
    time.sleep(5)
    seating_mat.skipAdv(ser)
        
    # Run until interrupted
    while True:
        if (event.is_set()):
            # Get map
            map = fitness_mat.getMap(ser)         
            # Get current timestamp
            current_timestamp = time.time()

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_FLOOR):
                csv_line.extend(map[row,:])

            csv_handler.write_sensor_data(FILEPATH_FLOOR1, csv_line)

        else:
            time.sleep(1)


def data_collector_floor2(port, event):
    # Connects to serial port
    ser = serial.Serial(
        port,
        baudrate=115200,
        timeout=0.1
    )

    # Skip BLE advertising string
    time.sleep(5)
    seating_mat.skipAdv(ser)
        
    # Run until interrupted
    while True:
        if (event.is_set()):
            # Get map
            map = fitness_mat.getMap(ser)   
            # Get current timestamp
            current_timestamp = time.time()

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_FLOOR):
                csv_line.extend(map[row,:])

            csv_handler.write_sensor_data(FILEPATH_FLOOR2, csv_line)
        else:
            time.sleep(1)


def data_collector_seat(port, event):
    # Connects to serial port
    ser = serial.Serial(
        port,
        baudrate=115200,
        timeout=0.1
    )

    # Skip BLE advertising string
    time.sleep(5)
    seating_mat.skipAdv(ser)
        
    # Run until interrupted
    while True:
        if (event.is_set()):
            # Send start sequence to retrieve full matrix
            seating_mat.fullMatrixStartSequence(ser)
            # Get matrix
            map = seating_mat.getMap(ser)
             
            # Get current timestamp
            current_timestamp = time.time()

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_SEAT):
                csv_line.extend(map[row,:])
            
            csv_handler.write_sensor_data(FILEPATH_SEAT, csv_line)
        else:
            time.sleep(1)

# TODO
# def click_restart_button():
#     st.session_state.restart_flag = True


def click_start_button():
    st.session_state.start_clicked = True
    st.session_state.stop_clicked = False

    st.session_state.start_disabled = True
    st.session_state.stop_disabled = False

    st.session_state.submit_button_flag = False


def click_stop_button():
    st.session_state.stop_clicked = True
    st.session_state.start_clicked = False

    st.session_state.start_disabled = True
    st.session_state.stop_disabled = False


def click_submit_button():
    st.session_state.submit_button_flag = True
    st.session_state.start_disabled = False


@st.cache_resource(
)
def init():
    st.session_state.init = True
    event = threading.Event()

    return event

@st.cache_resource(
)
def initialize_threads(_event, port1, port2):
    # Start each function in a separate thread
    thread1 = threading.Thread(target=data_collector_seat, args=(port1, _event,))
    thread2 = threading.Thread(target=data_collector_floor1, args=(port2, _event,))
    # thread3 = threading.Thread(target=data_collector_floor2, args=(port1, event,)

    # Start all threads
    thread1.start()
    thread2.start()
    # thread3.start()


def main():
    # Initialization
    if 'init' not in st.session_state:
        st.session_state.init = False
    if 'start_clicked' not in st.session_state:
        st.session_state.start_clicked = False
    if 'stop_clicked' not in st.session_state:
        st.session_state.stop_clicked = False
    if 'start_disabled' not in st.session_state:
        st.session_state.start_disabled = True
    if 'stop_disabled' not in st.session_state:
        st.session_state.stop_disabled = True
    if 'submit_disabled' not in st.session_state:
        st.session_state.submit_disabled = False
    if 'submit_button_flag' not in st.session_state:
        st.session_state.submit_button_flag = False

    # TODO
    # if 'restart_flag' not in st.session_state:
    #     st.session_state.restart_flag = False
    

    event = init()

    st.title('Time Up and Go Test') 
    st.markdown('1. Enter all ports and submit to start the collection process.')
    st.markdown('2. Press "Start" to begin data collection for **one** test.')
    st.markdown('3. Press "Stop" to end test and add identification. You can then enter the test participants initials and the test number to identify the collected data.')
    st.markdown('**OBS**. *To configure new ports, please restart the application!*')

    
    start_button_col, stop_button_col, submit_button_column, restart_button_column = st.columns([1, 3, 1, 1])
    with start_button_col:
        st.button('START', on_click=click_start_button, disabled=st.session_state.start_disabled)
    with stop_button_col:
        st.button('STOP', on_click=click_stop_button, disabled=st.session_state.stop_disabled)
    with submit_button_column:
        submit_button = st.button('Submit', on_click=click_submit_button, disabled=st.session_state.submit_disabled)
    # TODO
    # with restart_button_column:
    #     st.button('Restart App', on_click=click_restart_button)

 
    if st.session_state.init:
        text1_input_container = st.empty()
        text2_input_container = st.empty()
        # text3_input_container = st.empty()

        PORT_SEAT = text1_input_container.text_input('Enter port for seating mat:')
        PORT_FLOOR1 = text2_input_container.text_input('Enter port for fitness mat 1:')
        # PORT_FLOOR2 = text_3_input_container.text_input('Enter port for fitness mat 2:')
 
        if st.session_state.submit_button_flag: # NEW
            initialize_threads(event, PORT_SEAT, PORT_FLOOR1) 
            # initialize_threads(event, PORT_SEAT, PORT_FLOOR1, PORT_FLOOR2) 
            
            text1_input_container.empty()
            text2_input_container.empty()

            st.session_state.init = False
            st.session_state.start_disabled = False


    if st.session_state.start_clicked:
        csv_handler.delete(FILEPATH_SEAT)
        csv_handler.delete(FILEPATH_FLOOR1)
        # csv_handler.delete(FILEPATH_FLOOR2)

        csv_handler.create_csv_sensor_data(FILEPATH_SEAT, ROWS_SEAT, COLS_SEAT)
        csv_handler.create_csv_sensor_data(FILEPATH_FLOOR1, ROWS_FLOOR, COLS_FLOOR)
        # csv_handler.create_csv_sensor_data(FILEPATH_FLOOR2, ROWS_FLOOR, COLS_FLOOR)

        event.set()

    if st.session_state.stop_clicked:
        st.write('Stop button clicked! Press "Start" to run a new test.')
        event.clear() # Unset the event

        # Prompt the user to enter a new file name and the number of current test
        initials = st.text_input('Enter new file name:', value="Initials ")
        test = st.text_input('Enter new test number:', value="Number ")
        
        # Wait for the user to click the submit button
        if st.session_state.submit_button_flag:
            filepath_seat = f"MALISA_Python/sensor_data/{initials}_{test}_seat.csv"
            filepath_floor1 = f"MALISA_Python/sensor_data/{initials}_{test}_floor1.csv"
            # filepath_floor2 = f"MALISA_Python/sensor_data/{initials}_{test}_floor2.csv"

            csv_handler.change_name(FILEPATH_SEAT, filepath_seat)
            csv_handler.change_name(FILEPATH_FLOOR1, filepath_floor1)
            # csv_handler.change_name(FILEPATH_FLOOR2, filepath_floor2)

            st.session_state.stop_clicked = False
            st.session_state.submit_button_flag = False #NEW

    # TODO    
    # if st.session_state.restart_flag:
    #     st.session_state.restart_flag = False
    #     # Join the threads to wait for them to finish
    #     for thread in threads:
    #         thread.join()
    #     st.session_state.init = True

        
main()


