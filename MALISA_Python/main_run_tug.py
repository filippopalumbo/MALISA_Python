from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
import csv_handler
import streamlit as st
import time
import threading
import sensor_SW.seating_mat as seating_mat
import sensor_SW.fitness_mat as fitness_mat
import numpy as np
import serial

PORT_SEAT = '/dev/tty.usbserial-1120'
PORT_FLOOR1 = '/dev/tty.usbmodem84214601'  #CHANGE
PORT_FLOOR2 = '/dev/tty.usbserial-110'  #CHANGE
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
            if debug:
                print(f"Got map at {current_timestamp}")
            # if debug:
            #     printMap(map)

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_FLOOR):
                csv_line.extend(map[row,:])
            # if debug:
            #     print(csvLine)
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
            if debug:
                print(f"Got map at {current_timestamp}")
            # if debug:
            #     printMap(map)

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_FLOOR):
                csv_line.extend(map[row,:])
            # if debug:
            #     print(csvLine)
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
            if debug: #CHANGED
                print(f"Got map at {current_timestamp}")
            # if debug:
            #     printMap(map)

            # Prepare new CSV line
            csv_line = []
            csv_line.append(current_timestamp)
            for row in range(ROWS_SEAT):
                csv_line.extend(map[row,:])
            # if debug:
            #     print(csvLine)
            
            csv_handler.write_sensor_data(FILEPATH_SEAT, csv_line)
        else:
            time.sleep(1)


def click_start_button():
    st.session_state.start_clicked = True
    st.session_state.stop_clicked = False
    st.session_state.start_disabled = True
    st.session_state.stop_disabled = False


def click_stop_button():
    st.session_state.stop_clicked = True
    st.session_state.start_clicked = False
    st.session_state.start_disabled = False
    st.session_state.stop_disabled = True


@st.cache_resource(
)
def initialize_threads(port1, port2):
    # Create event 
    event = threading.Event()

    # Start each function in a separate thread
    thread1 = threading.Thread(target=data_collector_seat, args=(port1, event,))
    thread2 = threading.Thread(target=data_collector_floor1, args=(port2, event,))
    # thread3 = threading.Thread(target=data_collector_floor2, args=(port1, event,)

    # Start all threads
    thread1.start()
    thread2.start()
    # thread3.start()

    return event


def main():
    # Initialization
    if 'init' not in st.session_state:
        st.session_state.init = False
    if 'start_clicked' not in st.session_state:
        st.session_state.start_clicked = False
    if 'start_disabled' not in st.session_state:
        st.session_state.start_disabled = False
    if 'stop_clicked' not in st.session_state:
        st.session_state.stop_clicked = False
    if 'stop_disabled' not in st.session_state:
        st.session_state.stop_disabled = True
    
    event = initialize_threads(PORT_SEAT, PORT_FLOOR1)

    st.header('Time Up and Go Test') 
    st.button('START', on_click=click_start_button, disabled=st.session_state.start_disabled)
    st.button('STOP', on_click=click_stop_button, disabled=st.session_state.stop_disabled)

    if st.session_state.start_clicked:
        csv_handler.delete(FILEPATH_SEAT)
        csv_handler.delete(FILEPATH_FLOOR1)
        # csv_handler.delete(FILEPATH_FLOOR2)

        csv_handler.create_csv_sensor_data(FILEPATH_SEAT, ROWS_SEAT, COLS_SEAT)
        csv_handler.create_csv_sensor_data(FILEPATH_FLOOR1, ROWS_FLOOR, COLS_FLOOR)
        # csv_handler.create_csv_sensor_data(FILEPATH_FLOOR2, ROWS_FLOOR, COLS_FLOOR)

        event.set()

    if st.session_state.stop_clicked:
        st.write('Stop button clicked!')
        event.clear() # Unset the event

        # Prompt the user to enter a new file name and the number of current test
        initials = st.text_input('Enter new file name:', value="Initials ")
        test = st.text_input('Enter new test number:', value="Number ")

        # Display a button to signal that the input is complete
        submit_button = st.button('Submit')
        
        # Wait for the user to click the submit button
        if submit_button:
            filepath_seat = f"MALISA_Python/sensor_data/{initials}_{test}_seat.csv"
            filepath_floor1 = f"MALISA_Python/sensor_data/{initials}_{test}_floor1.csv"
            # filepath_floor2 = f"MALISA_Python/sensor_data/{initials}_{test}_floor2.csv"

            csv_handler.change_name(FILEPATH_SEAT, filepath_seat)
            csv_handler.change_name(FILEPATH_FLOOR1, filepath_floor1)
            # csv_handler.change_name(FILEPATH_FLOOR2, filepath_floor2)

            st.session_state.stop_clicked = False

        
main()


