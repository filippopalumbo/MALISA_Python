# TUG Test Analysis Application

This application is designed to analyze TUG (Timed Up and Go) test data collected from sensor floor mats. It provides functionalities to visualize the sensor data, run analysis algorithms, and display the results.

## To Run the Different Applications

1. **Run Sensor Data Collection App**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/app_sensor_data_collection.py
     ```
     For additional details and instructions, refer to the documentation within the file.
       
2. **Run Visual Analysis App**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/visual_analysis.py
     ```
     For additional details and instructions, refer to the documentation within the file.
     
3. **Run Main App - TUG Analysis**
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/app_main.py
     ```
     For additional details and instructions, refer to the documentation within the file.
     
Make sure you have all the requirements listed in `requirements.txt` installed.
```
Ensure the existence of the following directories: "sensor_data", "processed_data", "analyzed_data".
```

## Features

- **State Machine TUG Module**:
  - Select Mode: Choose between "Run Analysis" and "Visual Analysis" modes.
    - Run Analysis: Execute analysis algorithms on the selected TUG test data, and a CSV file will be generated.
    - Visual Analysis: View individual sensor frames and associated metrics.

- **Visual Analysis Module**:
  - Allows for visual analysis of sensor data frames and associated metrics.

## Contributors

- Malin Ramkull - Developer
- Hedda Eriksson - Developer
- Filippo Palumbo - Supervisor
