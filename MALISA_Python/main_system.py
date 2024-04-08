from sensor_calculations import *
from enumerations.tug_events import *
from enumerations.tug_states import *
from csv_handler import *
import streamlit as st
import threading 
import logging
import time

def thread_function(event):
    i = 0
    logging.info("Thread %s: starting", threading.gettrace)
    while not event.is_set():
        print("i: " + str(i))
        time.sleep(2)
        i+=1

    logging.info("Thread %s: finishing", threading.gettrace)
 

def click_start_button():
    st.session_state.start_clicked = True
    st.session_state.stop_clicked = False
    st.session_state.start_disabled = True
    st.session_state.stop_disabled = False
    st.session_state.thread_count += 1
    create_threads()

def click_stop_button():
    st.session_state.stop_clicked = True
    st.session_state.start_clicked = False
    st.session_state.start_disabled = False
    st.session_state.stop_disabled = True

@st.cache_resource(
)
def initialize_threads():
    event = threading.Event()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")
    thread = threading.Thread(target=thread_function, name = str(st.session_state.thread_count), args=(event,))
    logging.info("Main    : before running thread") 

    return thread, event

def create_threads():
    event = threading.Event()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")
    thread = threading.Thread(target=thread_function, name = str(st.session_state.thread_count), args=(event,))
    logging.info("Main    : before running thread") 

    return thread, event


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
    if 'thread_count' not in st.session_state:
        st.session_state.thread_count = 0

    thread, event = initialize_threads()


    st.button('START', on_click=click_start_button, disabled=st.session_state.start_disabled)
    st.button('STOP', on_click=click_stop_button, disabled=st.session_state.stop_disabled)

    if st.session_state.start_clicked:
        # The message and nested widget will remain on the page
        st.write('Start button clicked!')
        if st.session_state.thread_count != 1:
            thread, event = create_threads()
        thread.start()
        st.session_state.start_clicked = False

    if st.session_state.stop_clicked:
        # The message and nested widget will remain on the page
        st.write('Stop button clicked!')
        event.set()
        thread.join()

        for thread in threading.enumerate():
            print(f"Thread {thread.name} is alive")
        st.session_state.stop_clicked = False

main()


