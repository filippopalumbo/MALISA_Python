# TUG Test Analysis Application

This application is designed to analyze TUG (Timed Up and Go) test data collected from sensor floor mats. It provides functionalities to visualize the sensor data, run analysis algorithms, and display the results.

## To Run the Application

1. **Run State Machine TUG Module**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/state_machine.py
     ```
   
2. **Run Visual Analysis Module**:
   - Execute the following command in your terminal:
     ```
     streamlit run MALISA_Python/visual_analysis.py
     ```

Make sure you have all the requirements listed in `requirements.txt` installed.

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
