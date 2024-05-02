# TUG Test Analysis Application

This application is designed to analyze TUG (Timed Up and Go) test data collected from sensor floor mats. It provides functionalities to visualize the sensor data, run analysis algorithms, and display the results.

## To Run the Different Applications

1. **Run Sensor Data Collection App**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/app_sensor_data_collection.py
     ```
     For additional details and instructions, refer to the documentation within the file.
     
2. **Run Main App - TUG Analysis**
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/app_main.py
     ```
     or
     ```
     python -m streamlit run MALISA_Python\app_main.py
     ```
     For additional details and instructions, refer to the documentation within the file.

4. **Run Visual Analysis App**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/app_visual_analysis.py
     ```
     For additional details and instructions, refer to the documentation within the file.
     
Make sure you have all the requirements listed in `requirements.txt` installed.
```
Ensure the existence of the following directories: "sensor_data", "processed_data", "analyzed_data".
```

## Features

**Sensor Data Collection App**:
  - Collect raw data from two sensing mats and a sensing seat mat.
    - Used for TUG data collection.

**Main App - TUG Analysis**:
  - Analyzes the raw data and sends out information about TUG and gait parameters linked to a TUG test.

**Visual Analysis App**:
  - Allows for visual analysis of sensor data frames and associated metrics.

## Contributors

- Malin Ramkull - Developer
- Hedda Eriksson - Developer
- Filippo Palumbo - Supervisor
