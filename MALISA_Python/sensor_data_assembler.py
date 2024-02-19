import pandas as pd

# Read the CSV files into DataFrames
data_rug1 = pd.read_csv('/Users/heddaeriksson/Documents/GitHub/MALISA_Python/MALISA_Python/DS_TUG_Floor1')
data_rug2 = pd.read_csv('/Users/heddaeriksson/Documents/GitHub/MALISA_Python/MALISA_Python/DS_TUG_Floor2')

# Create a mirrored version of the selected part 
mirrored_data = data_rug2.iloc[:, ::-1]

# Merge the DataFrames horizontally using the 'Timestamp' column as the key
merged_data = pd.merge( mirrored_data, data_rug1, on='Timestamp', how='outer')

# Fill missing values with zeros
merged_data.fillna(0, inplace=True)

# Sort the DataFrame by the 'Timestamp' column
merged_data.sort_values(by='Timestamp', inplace=True)

# Optionally, save the merged and sorted DataFrame to a new CSV file
merged_data.to_csv('merged_data.csv', index=False)
